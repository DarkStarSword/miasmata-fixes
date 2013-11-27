#!/usr/bin/env python

import struct
import sys

import rs5
import miasmap

def parse_nlst_header(f):
	assert(f.read(10) == '\0\0NLST\0\0\1\0')
	(chunk_size, u1, num_entries, u2) = struct.unpack('<H6sH2s', f.read(12))
	assert(u1 == '\0'*6)
	assert(u2 == '\0'*2)
	return (chunk_size, num_entries)

def parse_mlst_header(f):
	assert(f.read(10) == '\0\0MLST\0\0\1\0')
	(chunk_size, u1) = struct.unpack('<H6s', f.read(8))
	assert(u1 == '\0'*6)
	return chunk_size

def parse_markers():
	f = open('markers')
	filesize = rs5.parse_raw_header(f)
	(chunk_size, num_entries) = parse_nlst_header(f)
	nlst = f.read(chunk_size).rstrip('\0').split('\0')
	chunk_size = parse_mlst_header(f)
	for i in range(chunk_size/6/4):
		(idx, u1, x, y, z, u2) = struct.unpack('<2I4f', f.read(6*4))
		yield (idx, nlst[idx], u1, x, y, z, u2)

def main():
	filters = sys.argv[1:]
	colours = ((128, 0, 0), (0, 128, 0), (0, 0, 128), (128, 128, 0), (128, 0, 128), (0, 128, 128), (128, 128, 128))
	for (idx, name, u1, x, y, z, u2) in parse_markers():
		c = (128, 128, 128)
		if filters:
			for (i, f) in enumerate(filters):
				if f in name:
					c = colours[i % len(colours)]
					break
			else:
				continue
		print '%25s (%.3i) %5i (%8.3f %8.3f %7.3f) %6.3f' % (name, idx, u1, x, y, z, u2)
		# miasmap.plot_cross(int(x), int(y))
		miasmap.plot_square(int(x), int(y), 20, c)
	miasmap.save_image('markers.jpg')

if __name__ == '__main__':
	main()
