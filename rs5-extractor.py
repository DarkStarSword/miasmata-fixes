#!/usr/bin/env python

# Based loosely on git://github.com/klightspeed/RS5-Extractor

# I wanted something a bit lower level that didn't convert the contained files
# so I could examine the format for myself. Don't expect this to be feature
# complete for a while

import struct
import zlib
import sys
import os
import collections

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

		# # NFI what this data is, probably just old data as things
		# # were moved around in the rs5 archive
		# print self.filename
		# i = 0
		# for x in data[40+filename_len+1:]:
		# 	print '%.2x' % ord(x),
		# 	i += 1
		# 	if (i % 32 == 0):
		# 		print
		# 	else:
		# 		if (i % 16 == 0):
		# 			print '',
		# 		if (i % 8 == 0):
		# 			print '',
		# 		if (i % 4 == 0):
		# 			print '',
		# print

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

class Rs5CompressedFileEncoder(object):
	def __init__(self, fp, filename):
		import rs5
		import StringIO
		self.modtime = os.stat(filename).st_mtime
		uncompressed = open(filename, 'rb').read()
		self.uncompressed_size = len(uncompressed)
		(self.type, self.filename, _1, _2) = rs5.parse_rs5file_header(StringIO.StringIO(uncompressed))
		compressed = zlib.compress(uncompressed)
		self.compressed_size = len(compressed)
		self.u1 = 0x30080000000
		self.u2 = 1

		self.data_off = fp.tell()
		fp.write(compressed)

	def gen_dir_ent(self):
		return struct.pack('<QIQ4sQQ',
				self.data_off, self.compressed_size, self.u1,
				self.type, self.uncompressed_size << 1 | self.u2,
				to_win_time(self.modtime)) + self.filename + '\0'


class Rs5ArchiveDecoder(collections.OrderedDict):
	def __init__(self, f):
		magic = f.read(8)
		if magic != 'CFILEHDR':
			print 'Invalid file header'
			return 1

		(d_off, ent_len, u1) = struct.unpack('<QII', f.read(16))
		# print hex(d_off), hex(ent_len)
		# print 'ent_len: %i' % ent_len
		# print "Unknown: %i" % u1
		#  - 0 in environment.rs5, 7 in main.rs5
		# Not enough samples to work out what this is...

		# print('0x%.8x - 0x%.8x  : %s' % (0, f.tell()-1, 'rs5 header'))
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
		# print 'd_len: %i, flags: %x' % (d_len, flags)

		collections.OrderedDict.__init__(self)

		for f_off in range(d_off + ent_len, d_off + d_len, ent_len):
			# print hex(f_off)
			try:
				entry = Rs5CompressedFile(f, f.read(ent_len))
				self[entry.filename] = entry
			except NotAFile:
				# XXX TODO FIXME: Figure out what these are
				continue

		# print('0x%.8x - 0x%.8x  : %s' % (d_off, f.tell()-1, 'directory'))

class Rs5ArchiveEncoder(collections.OrderedDict):
	header_len = 24
	ent_len = 168
	u1 = 0
	flags = 0x80000000

	def __init__(self, filename):
		collections.OrderedDict.__init__(self)
		self.fp = open(filename, 'wb')
		self.fp.seek(self.header_len)

	def add(self, filename):
		print "Adding %s..." % filename
		entry = Rs5CompressedFileEncoder(self.fp, filename)
		self[entry.filename] = entry

	def _write_directory(self):
		print "Writing central directory..."
		self.d_off = self.fp.tell()

		dir_hdr = struct.pack('<QII', self.d_off, self.ent_len * (1 + len(self)), self.flags)
		pad = '\0' * (self.ent_len - len(dir_hdr)) # XXX: Not sure if any data here is important
		self.fp.write(dir_hdr + pad)

		for file in self.itervalues():
			ent = file.gen_dir_ent()
			pad = '\0' * (self.ent_len - len(ent)) # XXX: Not sure if any data here is important
			self.fp.write(ent + pad)

	def _write_header(self):
		print "Writing RS5 header..."
		self.fp.seek(0)
		self.fp.write(struct.pack('<8sQII', 'CFILEHDR', self.d_off, self.ent_len, self.u1))

	def save(self):
		self._write_directory()
		self._write_header()
		self.fp.flush()
		print "Done."

def list_files(filename):
	rs5 = Rs5ArchiveDecoder(open(filename, 'rb'))
	for file in rs5.itervalues():
		print '%4s %8i %s' % (file.type, file.uncompressed_size, file.filename)

def extract(filename, dest, files):
	rs5 = Rs5ArchiveDecoder(open(filename, 'rb'))
	print 'Extracting files to %s' % dest
	for file in files:
		file = file.replace(os.path.sep, '\\')
		if file not in rs5:
			print '%s not found in %s!' % (file, filename)
			continue
		try:
			print 'Extracting %s %s...' % (repr(rs5[file].type), file)
			rs5[file].extract(dest)
		except OSError, e:
			print>>sys.stderr, 'ERROR EXTRACTING %s: %s, SKIPPING!' % (file.filename, str(e))

def extract_all(filename, dest):
	rs5 = Rs5ArchiveDecoder(open(filename, 'rb'))
	print 'Extracting files to %s' % dest
	for file in rs5.itervalues():
		if not file.filename:
			print 'SKIPPING FILE OF TYPE %s WITHOUT FILENAME' % repr(file.type)
			continue
		print 'Extracting %s %s...' % (repr(file.type), file.filename)
		try:
			file.extract(dest)
		except OSError, e:
			print>>sys.stderr, 'ERROR EXTRACTING %s: %s, SKIPPING!' % (file.filename, str(e))

def create_rs5(filename, source):
	if os.path.exists(filename):
		print '%s already exists, refusing to continue!' % filename
		return
	rs5 = Rs5ArchiveEncoder(filename)
	for (root, dirs, files) in os.walk(source):
		for file in files:
			rs5.add(os.path.join(root, file))
	rs5.save()

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
	group.add_argument('-l', '--list', action='store_true',
			help='List all files in the rs5 archive')
	group.add_argument('-x', '--extract', nargs='+', metavar=('FILES...'),
			help='Extract the specified FILES from the archive into the current directory')
	group.add_argument('-X', '--extract-all', metavar='DEST',
			help='Extract all files from the rs5 archive to DEST')
	group.add_argument('-C', '--create', metavar='SOURCE',
			help='Pack the files under SOURCE into a new RS5 file')

	group.add_argument('--analyse', metavar='RS5')

	parser.add_argument('-f', '--file', metavar='ARCHIVE', required=True,
			help='Specify the rs5 ARCHIVE to work on')

	return parser.parse_args()

def main():
	args = parse_args()

	if args.list:
		return list_files(args.file)

	if args.extract:
		return extract(args.file, '.', args.extract)

	if args.extract_all:
		return extract_all(args.file, args.extract_all)

	if args.create:
		return create_rs5(args.file, args.create)

	if args.analyse:
		return analyse(args.analyse)

if __name__ == '__main__':
	sys.exit(main())
