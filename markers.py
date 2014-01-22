#!/usr/bin/env python

import struct
import sys

import rs5file

def parse_nlst_header(f):
	(num_entries, u2) = struct.unpack('<H2s', f.read(4))
	assert(u2 == '\0'*2)
	return num_entries

def parse_markers(chunks):
	nlst = chunks['NLST']
	mlst = chunks['MLST']

	f = nlst.get_fp()
	num_entries = parse_nlst_header(f)
	nlst = f.read(nlst.size - 4).rstrip('\0').split('\0')

	f = mlst.get_fp()
	for i in range(mlst.size / 6 / 4):
		buf = f.read(6*4)
		(idx, u1, x, y, z, u2) = struct.unpack('<2I4f', buf)
		buf = ' '.join([ ''.join(reversed(buf[i:i+4])).encode('hex') for i in xrange(0, 6*4, 4)])
		yield (idx, nlst[idx], u1, x, y, z, u2, buf)

def main():
	import miasmap
	chunks = rs5file.Rs5ChunkedFileDecoder(open('markers').read())
	filters = sys.argv[1:]
	colours = ((128, 0, 0), (0, 128, 0), (0, 0, 128), (128, 128, 0), (128, 0, 128), (0, 128, 128), (128, 128, 128))
	for (idx, name, u1, x, y, z, u2, buf) in parse_markers(chunks):
		c = (128, 128, 128)
		if filters:
			for (i, f) in enumerate(filters):
				if f in name:
					c = colours[i % len(colours)]
					break
			else:
				continue
		print '%25s (%.3i) %5i (%8.3f %8.3f %7.3f) %6.3f %s  %.16f %.16f' % (name, idx, u1, x, y, z, u2, buf, x/8192.0, y/8192.0)
		# miasmap.plot_cross(int(x), int(y))
		miasmap.plot_square(int(x), int(y), 20, c)
	miasmap.save_image('markers.jpg')

if __name__ == '__main__':
	main()
