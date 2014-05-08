#!/usr/bin/env python

# Based loosely on git://github.com/klightspeed/RS5-Extractor

# I wanted something a bit lower level that didn't convert the contained files
# so I could examine the format for myself. Don't expect this to be feature
# complete for a while

try:
	from PySide import QtCore
except ImportError:
	class RS5Patcher(object):
		def tr(self, msg):
			return msg
else:
	# For PySide translations without being overly verbose...
	class RS5Patcher(QtCore.QObject): pass
RS5Patcher = RS5Patcher()

import struct
import zlib
import sys
import os
import collections
import rs5file

def progress(percent=None, msg=None):
	if msg is not None:
		print(msg)

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

class NotAFile(Exception): pass

class Rs5CompressedFile(object):
	def gen_dir_ent(self):
		return struct.pack('<QIQ4sQQ',
				self.data_off, self.compressed_size, self.u1,
				self.type, self.uncompressed_size << 1 | self.u2,
				to_win_time(self.modtime)) + self.filename + '\0'

	def read(self):
		self.fp.seek(self.data_off)
		return self.fp.read(self.compressed_size)

	def decompress(self):
		return zlib.decompress(self.read())


class Rs5CompressedFileDecoder(Rs5CompressedFile):
	def __init__(self, f, data):
		self.fp = f
		(self.data_off, self.compressed_size, self.u1, self.type, self.uncompressed_size,
				modtime) \
			= struct.unpack('<QIQ4sQQ', data[:40])

		self.u2 = self.uncompressed_size & 0x1
		if not self.u2:
			assert(self.data_off == 0)
			assert(self.compressed_size == 0)
			raise NotAFile()
		self.uncompressed_size >>= 1

		filename_len = data[40:].find('\0')
		self.filename = data[40:40 + filename_len]
		self.modtime = from_win_time(modtime)

	def extract(self, base_path, strip, overwrite):
		dest = os.path.join(base_path, self.filename.replace('\\', os.path.sep))
		if os.path.isfile(dest) and not overwrite: # and size != 0
			print>>sys.stderr, 'Skipping %s - file exists.' % dest
			return
		(dir, file) = os.path.split(dest)
		rs5file.mkdir_recursive(dir)
		f = open(dest, 'wb')
		try:
			data = self.decompress()
			if strip:
				contents = rs5file.Rs5FileDecoder(data)
				assert(contents.magic == self.type)
				assert(contents.filename == self.filename)
				assert(len(contents.data) == filesize)
				f.write(contents.data)
			else:
				f.write(data)
		except zlib.error as e:
			print>>sys.stderr, 'ERROR EXTRACTING %s: %s. Skipping decompression!' % (dest, str(e))
			f.write(self.read())
		f.close()
		os.utime(dest, (self.modtime, self.modtime))

	def extract_chunks(self, base_path, overwrite):
		data = self.decompress()

		try:
			chunks = rs5file.Rs5ChunkedFileDecoder(data)
		except:
			# print>>sys.stderr, 'NOTE: %s does not contain chunks, extracting whole file...' % dest
			return self.extract(base_path, False, overwrite)
		chunks.extract_chunks(base_path, overwrite, self.type)

class Rs5CompressedFileEncoder(Rs5CompressedFile):
	def __init__(self, fp, filename = None, buf = None, seek_cb = None):
		if filename is not None:
			self.modtime = os.stat(filename).st_mtime
			uncompressed = open(filename, 'rb').read()
		else:
			import time
			self.modtime = time.time()
			uncompressed = buf
		self.uncompressed_size = len(uncompressed)
		contents = rs5file.Rs5FileDecoder(uncompressed)
		(self.type, self.filename) = (contents.magic, contents.filename)
		compressed = zlib.compress(uncompressed)
		self.compressed_size = len(compressed)
		self.u1 = 0x30080000000
		self.u2 = 1
		self.fp = fp

		if seek_cb is not None:
			seek_cb(self.compressed_size)
		self.data_off = fp.tell()
		fp.write(compressed)

class Rs5CompressedFileRepacker(Rs5CompressedFile):
	def __init__(self, newfp, oldfile, seek_cb=None):
		self.compressed_size = oldfile.compressed_size
		self.u1 = oldfile.u1
		self.type = oldfile.type
		self.uncompressed_size = oldfile.uncompressed_size
		self.u2 = oldfile.u2
		self.modtime = oldfile.modtime
		self.filename = oldfile.filename
		self.fp = newfp

		if seek_cb is not None:
			seek_cb(self.compressed_size)
		self.data_off = newfp.tell()
		newfp.write(oldfile.read())

class Rs5CentralDirectory(collections.OrderedDict):
	@property
	def d_size(self):
		return self.ent_len * (1 + len(self))

class Rs5CentralDirectoryDecoder(Rs5CentralDirectory):
	def __init__(self, real_fp = None):
		self.fp.seek(self.d_off)
		data = self.fp.read(self.ent_len)
		(d_off1, self.d_orig_len, flags) = struct.unpack('<QII', data[:16])
		assert(self.d_off == d_off1)
		if real_fp is None:
			real_fp = self.fp

		collections.OrderedDict.__init__(self)

		for f_off in range(self.d_off + self.ent_len, self.d_off + self.d_orig_len, self.ent_len):
			try:
				entry = Rs5CompressedFileDecoder(real_fp, self.fp.read(self.ent_len))
				self[entry.filename] = entry
			except NotAFile:
				# XXX: Figure out what these are.
				# I think they are just deleted files
				continue

class Rs5CentralDirectoryEncoder(Rs5CentralDirectory):
	def write_directory(self):
		self.d_off = self.fp.tell()
		self.d_orig_len = self.d_size

		dir_hdr = struct.pack('<QII', self.d_off, self.d_size, self.flags)
		pad = '\0' * (self.ent_len - len(dir_hdr)) # XXX: Not sure if any data here is important
		self.fp.write(dir_hdr + pad)

		for file in self.itervalues():
			ent = file.gen_dir_ent()
			pad = '\0' * (self.ent_len - len(ent)) # XXX: Not sure if any data here is important
			self.fp.write(ent + pad)

class Rs5ArchiveDecoder(Rs5CentralDirectoryDecoder):
	def __init__(self, f):
		self.fp = f
		magic = f.read(8)
		if magic != 'CFILEHDR':
			raise ValueError('Invalid file header')

		(self.d_off, self.ent_len, self.u1) = struct.unpack('<QII', f.read(16))

		Rs5CentralDirectoryDecoder.__init__(self)

class Rs5ArchiveEncoder(Rs5CentralDirectoryEncoder):
	header_len = 24
	ent_len = 168
	u1 = 0
	flags = 0x80000000

	def __init__(self, filename):
		Rs5CentralDirectoryEncoder.__init__(self)
		self.fp = open(filename, 'wb')
		self.fp.seek(self.header_len)

	def add(self, filename, seek_cb=None, progress=progress):
		progress(msg=RS5Patcher.tr("Adding {0}...").format(filename))
		entry = Rs5CompressedFileEncoder(self.fp, filename, seek_cb=seek_cb)
		self[entry.filename] = entry

	def add_from_buf(self, buf, seek_cb=None, progress=progress):
		entry = Rs5CompressedFileEncoder(self.fp, buf=buf, seek_cb=seek_cb)
		progress(msg=RS5Patcher.tr("Adding {0}...").format(entry.filename))
		self[entry.filename] = entry

	def add_chunk_dir(self, path, seek_cb=None):
		print "Adding chunks from {0}...".format(path)
		files = sorted(os.listdir(path))
		files.remove('00-HEADER')
		header = open(os.path.join(path, '00-HEADER'), 'rb')
		header = rs5file.Rs5FileDecoder(header.read())
		chunks = collections.OrderedDict()
		for filename in files:
			chunk_path = os.path.join(path, filename)
			if not os.path.isfile(chunk_path) or '-' not in filename:
				print 'Skipping {0}: not a valid chunk'.format(chunk_path)
				continue
			chunk_name = filename.split('-', 1)[1]
			print '  {0}'.format(filename)
			chunk = open(chunk_path, 'rb')
			chunk = rs5file.Rs5ChunkEncoder(chunk_name, chunk.read())
			chunks[chunk.name] = chunk
		chunks = rs5file.Rs5ChunkedFileEncoder(header.magic, header.filename, header.u2, chunks)
		entry = Rs5CompressedFileEncoder(self.fp, buf=chunks.encode(), seek_cb=seek_cb)
		self[entry.filename] = entry

	def write_header(self, progress=progress):
		progress(msg=RS5Patcher.tr("Writing RS5 header..."))
		self.fp.seek(0)
		self.fp.write(struct.pack('<8sQII', 'CFILEHDR', self.d_off, self.ent_len, self.u1))

	def save(self, progress=progress):
		progress(msg=RS5Patcher.tr("Writing central directory..."))
		self.write_directory()
		self.write_header(progress=progress)
		self.fp.flush()
		progress(msg=RS5Patcher.tr("RS5 Written"))

class Rs5ArchiveUpdater(Rs5ArchiveEncoder, Rs5ArchiveDecoder):
	def __init__(self, fp):
		return Rs5ArchiveDecoder.__init__(self, fp)

	def seek_eof(self):
		self.fp.seek(0, 2)

	def seek_find_hole(self, size):
		'''Safe fallback version - always seeks to the end of file'''
		return self.seek_eof()

	def add(self, filename, progress=progress):
		return Rs5ArchiveEncoder.add(self, filename, seek_cb = self.seek_find_hole, progress=progress)

	def add_chunk_dir(self, path):
		return Rs5ArchiveEncoder.add_chunk_dir(self, path, seek_cb = self.seek_find_hole)

	def add_from_buf(self, buf, progress=progress):
		return Rs5ArchiveEncoder.add_from_buf(self, buf, seek_cb = self.seek_find_hole, progress=progress)

	def save(self, progress=progress):
		self.seek_find_hole(self.d_size)
		progress(msg=RS5Patcher.tr("Writing central directory..."))
		self.write_directory()
		# When updating an existing archive we use an extra flush
		# before writing the header to reduce the risk of writing a bad
		# header in case of an IO error, power failure, etc:
		self.fp.flush()
		self.write_header(progress=progress)
		self.fp.flush()
		progress(msg=RS5Patcher.tr("RS5 Written"))

# vi:noexpandtab:sw=8:ts=8
