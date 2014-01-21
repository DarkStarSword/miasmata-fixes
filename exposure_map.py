#!/usr/bin/env python

import sys
import os
import Image
import ImageDraw

size = 1024

def parse_exposure_map(exposure):
	global stream

	outline_mask = Image.new('1', (size, size))
	outline_mask_draw = ImageDraw.Draw(outline_mask)
	filledin_mask = Image.new('1', (size, size))
	filledin_mask_draw = ImageDraw.Draw(filledin_mask)
	overlayinfo_mask = Image.new('1', (size, size))
	overlayinfo_mask_draw = ImageDraw.Draw(overlayinfo_mask)

	extra = Image.new('L', (size, size))
	extra_draw = ImageDraw.Draw(extra)

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

		if val & 0x1:
			outline_mask_draw.rectangle((x, y, x+size-1, y+size-1), fill=1)
		if val & 0x2:
			filledin_mask_draw.rectangle((x, y, x+size-1, y+size-1), fill=1)
		if val & 0x4:
			overlayinfo_mask_draw.rectangle((x, y, x+size-1, y+size-1), fill=1)

		# No idea what the top bits are for - on two of my saves they
		# are always 0x70, but on a my save0 they are 0x38. They might
		# just be stack garbage, but save them away just in case:
		extra_draw.rectangle((x, y, x+size-1, y+size-1), fill=val)

	recurse_fill(0, 0, size, 0)
	assert(stream == 0)

	return (outline_mask, filledin_mask, overlayinfo_mask, extra)

def make_exposure_map(outline_mask, filledin_mask, overlayinfo_mask, extra):
	global stream, index

	outline_pix = outline_mask.load()
	filledin_pix = filledin_mask.load()
	overlay_pix = overlayinfo_mask.load()
	extra_pix = extra.load()

	stream = []
	index = 0

	def write_bit(v):
		global stream, index

		byte = index / 8
		bit = index % 8
		if bit == 0:
			stream.append(v << bit)
		else:
			stream[byte] |= v << bit
		index += 1

	def write_byte(v):
		for i in xrange(8):
			write_bit((v >> i) & 1)

	def calc_val(x, y):
		return (extra_pix[x, y] & 0xf8) | \
		      outline_pix[x, y]         | \
		     filledin_pix[x, y] << 1    | \
		      overlay_pix[x, y] << 2

	def need_recurse(x, y, size):
		val = calc_val(x, y)
		for y1 in xrange(y, y+size):
			for x1 in xrange(x, x+size):
				v1 = calc_val(x1, y1)
				if v1 != val:
					return True
		return False

	def recurse_compress(x, y, size, depth):
		while size > 1:
			if not need_recurse(x, y, size):
				write_bit(0)
				break
			write_bit(1)
			recurse_compress(x         , y         , size / 2, depth+1)
			recurse_compress(x + size/2, y         , size / 2, depth+1)
			recurse_compress(x         , y + size/2, size / 2, depth+1)
			size /= 2
			x += size
			y += size
		val = calc_val(x, y)
		write_byte(val)

	recurse_compress(0, 0, size, 0)

	return ''.join(map(chr, stream))

def compose_map(outline, outline_mask, filledin, filledin_mask, overlayinfo, overlayinfo_mask):
	image = Image.new('RGB', (size, size))
	draw = ImageDraw.Draw(image)

	if outline is None:
		outline = Image.new('RGB', (size, size), (255, 0, 0))

	image = Image.composite(outline, image, outline_mask)
	image = Image.composite(filledin, image, filledin_mask)
	image = Image.composite(overlayinfo, image, overlayinfo_mask)

	return image

def gen_map(exposure, filledin, overlayinfo):
	(outline_mask, filledin_mask, overlayinfo_mask, extra) = parse_exposure_map(exposure)

	image = compose_map(None, outline_mask, filledin, filledin_mask, overlayinfo, overlayinfo_mask)

	return (image, outline_mask, filledin_mask, overlayinfo_mask, extra)

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
	exposure_map = saves[sys.argv[1]]['player']['MAP']['exposure_map'].raw
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
	(image, outline_mask, filledin_mask, overlayinfo_mask, extra) = gen_map(exposure_map, filledin, overlayinfo)

	print 'Darkening...'
	image = Image.eval(image, lambda x: x/4)

	print 'Overlaying shoreline...'
	overlay_smap(image, shoreline, outline_mask, filledin_mask)

	print 'Saving exposure_map.png...'
	image.save('exposure_map.png')

	print 'Compressing exposure_map...'
	new_exposure_map = make_exposure_map(outline_mask, filledin_mask, overlayinfo_mask, extra)

	print 'Comparing...'
	assert(exposure_map == new_exposure_map)

	print 'Success'

if __name__ == '__main__':
	main()
