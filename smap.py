#!/usr/bin/env python

import os
import sys
import struct
import Image

import rs5file

def parse_smap_header(f):
	(magic, u1, num_entries, u2) = struct.unpack('<4s4sI4s', f.read(16))
	assert(magic == 'SMAP')
	assert(u1 == '\0\0\1\0')
	assert(u2 == '\0\0\0\0')
	return num_entries

def smap_iter(f, width):
	(magic, filename, filesize, u2) = rs5file.parse_rs5file_header(f)
	num_entries = parse_smap_header(f)
	smap = f.read(num_entries)

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

	f = open(sys.argv[1], 'r')

	for (i, (x, y)) in enumerate(smap_iter(f, width)):
		pix[x, y] = (255, 255, 255)

	image.save('smap_out.png')


if __name__ == '__main__':
	main()
