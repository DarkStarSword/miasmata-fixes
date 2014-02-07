#!/usr/bin/env python

import sys
import struct
import math
import Image

import rs5file

def main():
	f = open('cterr_hmap', 'rb')
	(magic, filename, filesize, u2) = rs5file.parse_rs5file_header(f)
	assert(magic == 'RAW.')
	assert(filename == 'cterr_hmap')
	assert(u2 == 0)

	w = h = int(math.sqrt(filesize / 4))
	image = Image.new('RGB', (w, h))
	pix = image.load()

	mn = -255
	mn2 = -32
	mn3 = -187
	mx = 255

	abs_mn = -2047.8125
	abs_mx = 1967.375
	for y in range(h):
		if y & 0xff == 0:
			print '%i/%i' % (y, h)
		floats = struct.unpack('<%if' % w, f.read(4*w))
		for x in range(w):
			z = floats[x]
			# (z,) = struct.unpack('<f', f.read(4))
			r = g = b = 0
			if z > 0:
				if z > mx:
					r = int(z * 255 / abs_mx)
				else:
					r = g = b = int(z)
			else:
				if z < mn:
					r = int(z * 255 / abs_mn)
				else:
					b = int(255 + z)
					g = int(255 - (z * 255 / mn2)) / 2
					if z <= mn3:
						r = g = 128
				# elif z > mn2:
				# 	b = int(255 - (z * 255 / mn2))
				# 	g = b / 2
				# else:
				# 	# b = int(255 + z)
				# 	b = int((z - mn2) * -255 / (255 + mn2))
			pix[x, y] = (r, g, b)
	image.transpose(Image.ROTATE_90).save('cterr_hmap.jpg')

if __name__ == '__main__':
	main()

# vi:noexpandtab:sw=8:ts=8
