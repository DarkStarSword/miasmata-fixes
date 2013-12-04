#!/usr/bin/env python

import sys
import os
import Image
import ImageDraw

import smap

def main():
	global stream

	size = 1024
	image = Image.new('RGB', (size, size))
	pix = image.load()
	draw = ImageDraw.Draw(image)

	data = open(sys.argv[1]).read()
	stream = 0
	for i in range(len(data)):
		stream |= ord(data[i]) << (8*i)
	# print hex(stream)

	def recurse_fill(x, y, size, depth):
		global stream

		while size > 1:
			# print '%s(%i, %i, %i)' % (' '*depth, x, y, size)
			bit = stream & 1
			stream >>= 1
			if not bit:
				break
			recurse_fill(x         , y         , size / 2, depth+1)
			recurse_fill(x + size/2, y         , size / 2, depth+1)
			recurse_fill(x         , y + size/2, size / 2, depth+1)
			size /= 2
			x += size
			y += size
		val = stream & 0xff
		stream >>= 8
		# print '%s Fill (%i, %i, %i, %i) with %.2x' % (' '*depth, x, y, x+size, y+size, val)
		r = g = b = (val & 0x07) << 5
		r = g = b = 0
		if val & 0x1:
			r = 32
		if val & 0x2:
			g = 32
		if val & 0x4:
			b = 32

		# These bits never seem to change, not sure what 0x40 is:
		# assert(val & 0xb8 != 0xb8)
		col = (r, g, b)
		draw.rectangle((x, y, x+size, y+size), outline=col, fill=col)

	recurse_fill(0, 0, size, 0)

	revealed = 0
	sf = open('extracted/player_map_achievements', 'rb')
	for (total, (x, y)) in enumerate(smap.smap_iter(sf, size), 1):
		(r, g, b) = pix[x, y]
		if g:
			r = g = b = 64
			revealed += 1
		elif r or b:
			r = 255
			g = 200
			b = 64
		pix[x, y] = (r, g, b)

	print '%i / %i (%i%%) of the coast mapped' % (revealed, total, revealed * 100 / total)

	image.save('test.png')
	# print 'Remaining:', hex(stream)
	assert(stream == 0)


if __name__ == '__main__':
	main()
