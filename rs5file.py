#!/usr/bin/env python

import struct
import sys
import collections
from StringIO import StringIO

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

def enc_header(magic, name, size, u2):
	name = name + '\0'
	ret = struct.pack('<4s2sBBI', magic, '\0\0', len(name), u2, size)
	ret += name + padding(12 + len(name), 8)
	return ret

def enc_file(magic, name, data, u2):
	header = enc_header(magic, name, len(data), u2)
	return header + data + padding(len(data), 8)


class Rs5Chunk(object):
	u1 = '\0\0\1'
	u3 = '\0\0\0\0'

	def encode(self):
		header = struct.pack('<4s3sBI4s', self.name, self.u1,
				int(self.size == 0), self.size, self.u3)
		return header + self.data + padding(self.size, 8)

class Rs5ChunkDecoder(Rs5Chunk):
	def __init__(self, fp):
		self.fp = fp
		header = fp.read(16)
		if header == '':
			raise EOFError()
		(self.name, u1, u2, self.size, u3) = \
				struct.unpack('<4s3sBI4s', header)
		assert(u1 == self.u1)
		assert(u2 == int(self.size == 0))
		assert(u3 == self.u3)
		self.data_off = fp.tell()

		fp.seek(self.size, 1)
		pad_len = padding_len(self.size, 8)
		assert(fp.read(pad_len) == '\0'*pad_len)

	def get_fp(self):
		self.fp.seek(self.data_off)
		return self.fp

	@property
	def data(self):
		return self.get_fp().read(self.size)

class Rs5ChunkEncoder(Rs5Chunk):
	def __init__(self, name, data):
		self.name = name
		self.size = len(data)
		self.data = data
		self.data_off = 0



class Rs5File(object):
	def header(self):
		return enc_header(self.magic, self.filename, len(self.data), self.u2)

	def encode(self):
		return enc_file(self.magic, self.filename, self.data, self.u2)

class Rs5FileDecoder(Rs5File):
	def __init__(self, data):
		self.fp = data
		if not isinstance(data, file):
			self.fp = StringIO(data)
		(self.magic, self.filename, self.filesize, self.u2) = parse_rs5file_header(self.fp)
		self.data_off = self.fp.tell()

	@property
	def data(self):
		self.fp.seek(self.data_off)
		return self.fp.read(self.filesize)

class Rs5FileEncoder(Rs5File):
	def __init__(self, magic, name, data, u2):
		self.magic = magic
		self.filename = name
		if data is not None:
			self.data = data
		self.u2 = u2


class Rs5ChunkedFile(Rs5File, collections.OrderedDict):
	pass

class Rs5ChunkedFileDecoder(Rs5FileDecoder, Rs5ChunkedFile):
	def __init__(self, data):
		Rs5FileDecoder.__init__(self, data)
		collections.OrderedDict.__init__(self)

		while True:
			try:
				chunk = Rs5ChunkDecoder(self.fp)
				self[chunk.name] = chunk
			except EOFError:
				if self == {}:
					raise
				break

class Rs5ChunkedFileEncoder(Rs5FileEncoder, Rs5ChunkedFile):
	def __init__(self, magic, name, u2, chunks):
		Rs5FileEncoder.__init__(self, magic, name, None, u2)
		if not isinstance(chunks, dict):
			chunks = {chunks.name: chunks}
		collections.OrderedDict.__init__(self, chunks)

	@property
	def data(self):
		r = ''
		for chunk in self.itervalues():
			r += chunk.encode()
		return r


def rs5_file_decoder_factory(data):
	try:
		return Rs5ChunkedFileDecoder(data)
	except:
		return Rs5FileDecoder(data)

def create_header_chunk(magic, name):
	# NOTE: This will create a header with a filesize of 0, which is ok
	# when used in a chunk directory as it is ignored, but shouldn't be
	# used directly inside an rs5 archive file.
	sys.stdout.write(enc_header(magic, name, 0, 1))

if __name__ == '__main__':
	if len(sys.argv) != 3:
		print 'Creates a local file header suitable for use as 00-HEADER'
		print 'in a chunk directory. WARNING: filesize will be 0 and'
		print 'the resulting header should not be used directly!'
		print
		print 'usage: %s type filename > 00-HEADER' % sys.argv[0]
		sys.exit(1)
	sys.exit(create_header_chunk(sys.argv[1], sys.argv[2]))

# vi:noexpandtab:sw=8:ts=8
