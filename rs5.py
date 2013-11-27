#!/usr/bin/env python

import struct
import sys

def parse_raw_header(f):
	(magic, u1, filename_len, u2, filesize) = struct.unpack('<4s2sB1sI', f.read(12))
	if magic != 'RAW.':
		raise ValueError()
	assert(u1 == '\0\0')
	# assert(u2 == '\0')
	print>>sys.stderr, 'Parsing RAW %s...' % f.read(filename_len).rstrip('\0')
	assert(f.read(2) == '\0\0')
	return filesize

def parse_header(f):
	# Based on parse_inod_header
	(magic, u1, filename_len, u2, filesize) = struct.unpack('<4s2sBBI', f.read(12))
	assert(u1 == '\0\0')
	filename = f.read(filename_len).rstrip('\0')
	print>>sys.stderr, 'Parsing header %s %s (u=%i)...' % (magic, filename, u2)
	pad = (8 - ((12 + filename_len) % 8)) % 8
	# print>>sys.stderr, '%i bytes of padding' % pad
	assert(f.read(pad) == '\0'*pad)
	return (magic, filename, filesize)
