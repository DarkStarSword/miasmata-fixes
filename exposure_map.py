#!/usr/bin/env python

import sys
import os
import Image
import ImageDraw

def gen_map(exposure, filledin, overlayinfo):
	global stream

	size = 1024
	image = Image.new('RGB', (size, size))
	draw = ImageDraw.Draw(image)

	outline_mask = Image.new('1', (size, size))
	outline_mask_draw = ImageDraw.Draw(outline_mask)
	filledin_mask = Image.new('1', (size, size))
	filledin_mask_draw = ImageDraw.Draw(filledin_mask)
	overlayinfo_mask = Image.new('1', (size, size))
	overlayinfo_mask_draw = ImageDraw.Draw(overlayinfo_mask)

	stream = 0
	for i in range(len(exposure)):
		stream |= ord(exposure[i]) << (8*i)

	def recurse_fill(x, y, size, depth):
		global stream

		while size > 1:
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
		r = g = b = 0
		if val & 0x1:
			r = 255 # 64
			outline_mask_draw.rectangle((x, y, x+size-1, y+size-1),  fill=1)
		if val & 0x2:
			g = 32
			filledin_mask_draw.rectangle((x, y, x+size-1, y+size-1),  fill=1)
		if val & 0x4:
			b = 32
			overlayinfo_mask_draw.rectangle((x, y, x+size-1, y+size-1), fill=1)

		# These bits never seem to change, not sure what 0x40 is:
		# assert(val & 0xb8 != 0xb8)
		col = (r, g, b)
		draw.rectangle((x, y, x+size-1, y+size-1), outline=col, fill=col)

	recurse_fill(0, 0, size, 0)
	assert(stream == 0)

	image = Image.composite(filledin, image, filledin_mask)
	image = Image.composite(overlayinfo, image, overlayinfo_mask)

	return (image, outline_mask, filledin_mask)

def overlay_smap(image, shoreline, outline_mask, filledin_mask):
	import smap
	revealed = 0
	pix = image.load()
	outline_pix = outline_mask.load()
	filledin_pix = filledin_mask.load()

	for (total, (x, y)) in enumerate(smap.smap_iter(shoreline, image.size[0]), 1):
		if filledin_pix[x, y]:
			r = g = b = 80
			revealed += 1
		else:
			r = 255
			g = 200
			b = 64
		pix[x, y] = (r, g, b)

	print '%i / %i (%i%%) of the coast mapped' % (revealed, total, revealed * 100 / total)

def main():
	import rs5archive, rs5file, data, imag
	print 'Opening saves.dat...'
	saves = open('saves.dat', 'rb')
	print 'Procesing saves.dat...'
	saves = data.parse_data(saves)
	exposure_map = str(saves[sys.argv[1]]['player']['MAP']['exposure_map'])
	print 'Opening main.rs5...'
	archive = rs5archive.Rs5ArchiveDecoder(open('main.rs5', 'rb'))

	print 'Extracting Map_FilledIn...'
	filledin = rs5file.Rs5ChunkedFileDecoder(archive['TEX\\Map_FilledIn'].decompress())
	print 'Decoding Map_FilledIn...'
	filledin = imag.open_rs5file_imag(filledin, (1024, 1024), 'RGB')

	print 'Extracting Map_OverlayInfo...'
	overlayinfo = rs5file.Rs5ChunkedFileDecoder(archive['TEX\\Map_OverlayInfo'].decompress())
	print 'Decoding Map_OverlayInfo...'
	overlayinfo = imag.open_rs5file_imag(overlayinfo, (1024, 1024), 'RGB')

	print 'Extracting player_map_achievements...' # XXX: Also in environment.rs5
	shoreline = rs5file.Rs5ChunkedFileDecoder(archive['player_map_achievements'].decompress())

	print 'Generating map...'
	(image, outline_mask, filledin_mask) = gen_map(exposure_map, filledin, overlayinfo)

	print 'Darkening...'
	image = Image.eval(image, lambda x: x/4)

	print 'Overlaying shoreline...'
	overlay_smap(image, shoreline, outline_mask, filledin_mask)

	print 'Saving exposure_map.png...'
	image.save('exposure_map.png')


if __name__ == '__main__':
	main()
