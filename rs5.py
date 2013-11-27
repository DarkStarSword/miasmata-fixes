#!/usr/bin/env python

import struct
import sys

def parse_raw_header(f): # XXX: Deprecated - use parse_rs5file_header
	(magic, u1, filename_len, u2, filesize) = struct.unpack('<4s2sB1sI', f.read(12))
	if magic != 'RAW.':
		raise ValueError()
	assert(u1 == '\0\0')
	# assert(u2 == '\0')
	print>>sys.stderr, 'Parsing RAW %s...' % f.read(filename_len).rstrip('\0')
	assert(f.read(2) == '\0\0')
	return filesize

def padding_len(pos, alignment):
	return (alignment - (pos % alignment)) % alignment

def padding(pos, alignment):
	return '\0' * padding_len(pos, alignment)

def parse_rs5file_header(f):
	# Based on parse_inod_header
	(magic, u1, filename_len, u2, filesize) = struct.unpack('<4s2sBBI', f.read(12))
	assert(u1 == '\0\0')
	filename = f.read(filename_len).rstrip('\0')
	# print>>sys.stderr, 'Parsing header %s %s (u=%i)...' % (magic, filename, u2)
	pad = padding_len(12 + filename_len, 8)
	# print>>sys.stderr, '%i bytes of padding' % pad
	assert(f.read(pad) == '\0'*pad)
	return (magic, filename, filesize, u2)

def _enc_header(magic, name, size, u2):
	name = name + '\0'
	ret = struct.pack('<4s2sBBI', magic, '\0\0', len(name), u2, size)
	ret += name + padding(12 + len(name), 8)
	return ret

def enc_file(magic, name, data, u2):
	header = _enc_header(magic, name, len(data), u2)
	return header + data + padding(len(data), 8)

class Rs5File(object):
	pass

class Rs5FileDecoder(Rs5File):
	def __init__(self, f):
		pos = f.tell()
		(self.magic, self.filename, self.filesize, self.u2) = parse_rs5file_header(f)
		self.headersize = f.tell() - pos
