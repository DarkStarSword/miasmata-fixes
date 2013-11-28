#!/usr/bin/env python

import os
import sys
import struct
import Image

import rs5

def parse_smap_header(f):
	(magic, u1, num_entries, u2) = struct.unpack('<4s4sI4s', f.read(16))
	assert(magic == 'SMAP')
	assert(u1 == '\0\0\1\0')
	assert(u2 == '\0\0\0\0')
	return num_entries


def main():
	width = height = 1024

	highlight = [ int(x, 16) for x in sys.argv[2:] ]

	f = open(sys.argv[1], 'r')
	(magic, filename, filesize, u2) = rs5.parse_rs5file_header(f)
	num_entries = parse_smap_header(f)
	smap = f.read(num_entries)

	image = Image.new('RGB', (width, height))
	image = Image.open('Map_FilledIn.jpg').resize((width, height))
	image = Image.eval(image, lambda x: x/8)
	pix = image.load()

	off = 0
	c = (255, 255, 255)
	if highlight:
		c = (0, 0, 64)
	for (i, inc) in enumerate(map(ord, smap)):
		off += inc
		if inc < 0xff:
			if i in highlight:
				print i, hex(off)
				pix[off % width, off / width] = (255, 255, 255)
			else:
				pix[off % width, off / width] = c

	image.save('%s.png' % filename)


if __name__ == '__main__':
	main()
