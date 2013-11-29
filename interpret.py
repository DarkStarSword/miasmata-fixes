#!/usr/bin/env python

import sys
import struct

def main():
	f = open(sys.argv[1])
	fmt = sys.argv[2]
	size = struct.calcsize(fmt)
	while True:
		d = f.read(size)
		if len(d) < size:
			rem = [c.encode('hex_codec') for c in d]
			print
			print ' '.join(['--']*len(rem))
			print ' '.join(rem)
			return
		print '\t'.join(map(str, struct.unpack(fmt, d)))


if __name__ == '__main__':
	main()
