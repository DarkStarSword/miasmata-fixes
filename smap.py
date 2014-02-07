#!/usr/bin/env python

import os
import sys
import struct
import Image

import rs5file


def smap_iter(f, width):
	smap = f['SMAP'].data

	off = 0
	for (i, inc) in enumerate(map(ord, smap)):
		off += inc
		if inc < 0xff:
			yield (off % width, off / width)

def main():
	width = height = 1024

	image = Image.new('RGB', (width, height))
	image = Image.open('Map_FilledIn.jpg').resize((width, height))
	image = Image.eval(image, lambda x: x/8)
	pix = image.load()

	f = rs5file.Rs5ChunkedFileDecoder(open(sys.argv[1], 'rb').read())

	for (x, y) in smap_iter(f, width):
		pix[x, y] = (255, 255, 255)

	image.save('smap_out.png')


if __name__ == '__main__':
	main()

# vi:noexpandtab:sw=8:ts=8
