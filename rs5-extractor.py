#!/usr/bin/env python

# Based loosely on git://github.com/klightspeed/RS5-Extractor

# I wanted something a bit lower level that didn't convert the contained files
# so I could examine the format for myself. Don't expect this to be feature
# complete and a re-packer is probably a long way off.

import struct
import zlib
import sys
import os

# http://msdn.microsoft.com/en-us/library/system.datetime.fromfiletimeutc.aspx:
# A Windows file time is a 64-bit value that represents the number of
# 100-nanosecond intervals that have elapsed since 12:00 midnight,
# January 1, 1601 A.D. (C.E.) Coordinated Universal Time (UTC).
import calendar
win_epoch = calendar.timegm((1601, 1, 1, 0, 0, 0))
def from_win_time(win_time):
	return win_time / 10000000 + win_epoch
def to_win_time(unix_time):
	return (unix_time - win_epoch) * 10000000

def mkdir_recursive(path):
	if path == '':
		return
	(head, tail) = os.path.split(path)
	mkdir_recursive(head)
	if not os.path.exists(path):
		os.mkdir(path)
	elif not os.path.isdir(path):
		raise OSError(17, '%s exists but is not a directory' % path)

class NotAFile(Exception): pass

class Rs5CompressedFile(object):
	def __init__(self, f, data):
		self.fp = f
		(self.data_off, self.compressed_size, self.u1, self.type, self.uncompressed_size,
				modtime) \
			= struct.unpack('<QIQ4sQQ', data[:40])

		self.u2 = self.uncompressed_size & 0x1
		if not self.u2:
			raise NotAFile()
		self.uncompressed_size >>= 1

		filename_len = data[40:].find('\0')
		self.filename = data[40:40 + filename_len]
		self.modtime = from_win_time(modtime)
		# print repr(self.type), self.filename
		# print hex(self.data_off), hex(self.compressed_size)

		# print hex(unknown1), hex(unknown2)
		# # assert(unknown1 == 0x30080000000)
		# if unknown1 != 0x30080000000:
		# 	print repr(self.type), self.filename
		# 	print hex(unknown1), hex(unknown2)

	def _read(self):
		self.fp.seek(self.data_off)
		return self.fp.read(self.compressed_size)

	def decompress(self):
		return zlib.decompress(self._read())

	def extract(self, base_path):
		dest = os.path.join(base_path, self.filename.replace('\\', os.path.sep))
		if os.path.isfile(dest): # and size != 0
			print>>sys.stderr, 'Skipping %s - file exists.' % dest
			return
		(dir, file) = os.path.split(dest)
		mkdir_recursive(dir)
		f = open(dest, 'wb')
		try:
			f.write(self.decompress())
		except zlib.error, e:
			print>>sys.stderr, 'ERROR EXTRACTING %s: %s. Skipping decompression!' % (dest, str(e))
			f.write(self._read())
		f.close()
		os.utime(dest, (self.modtime, self.modtime))


class Rs5Archive(list):
	pass

class Rs5ArchiveDecoder(Rs5Archive):
	def __init__(self, f):
		magic = f.read(8)
		if magic != 'CFILEHDR':
			print 'Invalid file header'
			return 1

		(d_off, ent_len, u1) = struct.unpack('<QII', f.read(16))
		# print hex(d_off), hex(ent_len)
		# print "Unknown: %i" % u1
		#  - 0 in environment.rs5, 7 in main.rs5
		# Not enough samples to work out what this is...

		print('0x%.8x - 0x%.8x  : %s' % (0, f.tell()-1, 'rs5 header'))
		# XXX: What is the data following this header?
		# XXX: The files are in this range, but what else?
		# i = 0
		# while f.tell() != d_off:
		# 	print '%.2x' % ord(f.read(1)),
		# 	if (i % 32 == 0):
		# 		print
		# 		print '0x%.8x: ' % f.tell(),
		# 	else:
		# 		if (i % 16 == 0):
		# 			print '',
		# 		if (i % 8 == 0):
		# 			print '',
		# 		if (i % 4 == 0):
		# 			print '',
		# 	i += 1
		# print

		f.seek(d_off)
		data = f.read(ent_len)
		(d_off1, d_len, flags) = struct.unpack('<QII', data[:16])
		assert(d_off == d_off1)
		# print hex(d_len), hex(flags)

		Rs5Archive.__init__(self)

		for f_off in range(d_off + ent_len, d_off + d_len, ent_len):
			# print hex(f_off)
			try:
				self.append(Rs5CompressedFile(f, f.read(ent_len)))
			except NotAFile:
				# XXX TODO FIXME: Figure out what these are
				continue

		print('0x%.8x - 0x%.8x  : %s' % (d_off, f.tell()-1, 'directory'))

def extract_all(filename, dest):
	rs5 = Rs5ArchiveDecoder(open(filename, 'rb'))
	print 'Extracting files to %s' % dest
	for file in rs5:
		if not file.filename:
			print 'SKIPPING FILE OF TYPE %s WITHOUT FILENAME' % repr(file.type)
			continue
		print 'Extracting %s %s...' % (repr(file.type), file.filename)
		try:
			file.extract(dest)
		except OSError, e:
			print>>sys.stderr, 'ERROR EXTRACTING %s: %s, SKIPPING!' % (file.filename, str(e))

def analyse(filename):
	rs5 = Rs5ArchiveDecoder(open(filename, 'rb'))
	import rs5 as foo
	import StringIO
	interesting = ('cterr_texturelist',)
	for file in rs5:
		if not file.filename:
			# XXX: What are these?
			# print 'SKIPPING FILE OF TYPE %s WITHOUT FILENAME' % repr(file.type)
			continue
		try:
			d = file.decompress()
			size = len(d)
			d = StringIO.StringIO(d)
		except zlib.error, e:
			# XXX: What are these?
			print 'ERROR EXTRACTING %s: %s' % (file.filename, str(e))
			print '%s %x %8i %x    |   %-25s  |  compressed_size: %i' \
				% (file.type, file.u1, file.uncompressed_size, file.u2, file.filename, file.compressed_size)
			if file.filename in interesting:
				continue
			raise
			# continue
		rs5file = foo.Rs5FileDecoder(d)
		# if file.filename in interesting:
		if True:
			print '0x%.8x - 0x%.8x  |  %s %x %8i %x %x  |   %-25s  |  compressed_size: %i\t|  size: %8i' \
				% (file.data_off, file.data_off + file.compressed_size-1, file.type, file.u1, file.uncompressed_size, file.u2, rs5file.u2, file.filename, file.compressed_size, rs5file.filesize+rs5file.headersize)

		assert(file.u2 == 1)
		assert(file.uncompressed_size == size)
		assert(file.type == rs5file.magic)
		assert(file.filename == rs5file.filename)

		# ALIGNMENT CONSTRAINT FOUND - FILE IS PADDED TO 8 BYTES BEFORE COMPRESSION
		assert(file.uncompressed_size % 8 == 0)

		# PADDING CONSTRAINT - FILE HEADER IS PADDED TO A MULTIPLE OF 8 BYTES
		assert(rs5file.headersize % 8 == 0)

		# NO PADDING CONSTRAINTS FOUND ON CONTAINED FILES IN THE GENERAL CASE
		# assert(rs5file.filesize % 2 == 0)
		# assert(rs5file.filesize % 4 == 0)
		# assert(rs5file.filesize % 8 == 0)
		#assert((rs5file.headersize + rs5file.filesize) % 2 == 0)
		#assert((rs5file.headersize + rs5file.filesize) % 4 == 0)
		#assert((rs5file.headersize + rs5file.filesize) % 8 == 0)
		#assert((rs5file.headersize + rs5file.filesize) % 16 == 0)

		# AT LEAST 'DATA' SUBTYPE DOES HAVE AN 8 BYTE PADDING
		if file.type == 'RAW.':
			t = d.read(4)
			# print '%s\t%s' % (repr(t), file.filename)
			if t == 'DATA':
				assert(rs5file.filesize % 8 == 0)
				assert((rs5file.headersize + rs5file.filesize) % 8 == 0)


def parse_args():
	import argparse
	parser = argparse.ArgumentParser()

	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('-X', '--extract-all', nargs=2, metavar=('RS5', 'DEST'),
			help='Extract all files from the rs5 archive to DEST')

	group.add_argument('--analyse', metavar='RS5')

	return parser.parse_args()

def main():
	args = parse_args()

	if args.extract_all:
		return extract_all(*args.extract_all)

	if args.analyse:
		return analyse(args.analyse)

if __name__ == '__main__':
	sys.exit(main())
