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
import rs5file

chunk_extensions = {
	('IMAG', 'DATA'): '.dds',
}

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
	def gen_dir_ent(self):
		return struct.pack('<QIQ4sQQ',
				self.data_off, self.compressed_size, self.u1,
				self.type, self.uncompressed_size << 1 | self.u2,
				to_win_time(self.modtime)) + self.filename + '\0'

class Rs5CompressedFileDecoder(Rs5CompressedFile):
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

	def _read(self):
		self.fp.seek(self.data_off)
		return self.fp.read(self.compressed_size)

	def decompress(self):
		return zlib.decompress(self._read())

	def extract(self, base_path, strip, overwrite):
		dest = os.path.join(base_path, self.filename.replace('\\', os.path.sep))
		if os.path.isfile(dest) and not overwrite: # and size != 0
			print>>sys.stderr, 'Skipping %s - file exists.' % dest
			return
		(dir, file) = os.path.split(dest)
		mkdir_recursive(dir)
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
			f.write(self._read())
		f.close()
		os.utime(dest, (self.modtime, self.modtime))

	def extract_chunks(self, base_path, overwrite):
		dest = os.path.join(base_path, self.filename.replace('\\', os.path.sep))
		data = self.decompress()

		try:
			chunks = rs5file.Rs5ChunkedFileDecoder(data)
		except:
			# print>>sys.stderr, 'NOTE: %s does not contain chunks, extracting whole file...' % dest
			return self.extract(base_path, False, overwrite)

		if os.path.exists(dest) and not os.path.isdir(dest):
			print>>sys.stderr, 'WARNING: %s exists, but is not a directory, skipping!' % dest
			return
		mkdir_recursive(dest)

		path = os.path.join(dest, '00-HEADER')
		if os.path.isfile(path) and not overwrite: # and size != 0
			print>>sys.stderr, 'Skipping %s - file exists.' % dest
		else:
			f = open(path, 'wb')
			f.write(chunks.header())
			f.close()

		for (i, chunk) in enumerate(chunks.itervalues(), 1):
			extension = (self.type, chunk.name)
			path = os.path.join(dest, '%.2i-%s%s' % (i, chunk.name, chunk_extensions.get(extension, '')))
			if os.path.isfile(path) and not overwrite: # and size != 0
				print>>sys.stderr, 'Skipping %s - file exists.' % dest
				continue
			f = open(path, 'wb')
			f.write(chunk.data)
			f.close()

class Rs5CompressedFileEncoder(Rs5CompressedFile):
	def __init__(self, fp, filename = None, buf = None):
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

		self.data_off = fp.tell()
		fp.write(compressed)

class Rs5CompressedFileRepacker(Rs5CompressedFile):
	def __init__(self, newfp, oldfile):
		self.compressed_size = oldfile.compressed_size
		self.u1 = oldfile.u1
		self.type = oldfile.type
		self.uncompressed_size = oldfile.uncompressed_size
		self.u2 = oldfile.u2
		self.modtime = oldfile.modtime
		self.filename = oldfile.filename

		self.data_off = newfp.tell()
		newfp.write(oldfile._read())


class Rs5Archive(collections.OrderedDict):
	pass

class Rs5ArchiveDecoder(Rs5Archive):
	def __init__(self, f):
		self.fp = f
		magic = f.read(8)
		if magic != 'CFILEHDR':
			raise ValueError('Invalid file header')

		(self.d_off, self.ent_len, u1) = struct.unpack('<QII', f.read(16))

		f.seek(self.d_off)
		data = f.read(self.ent_len)
		(d_off1, self.d_len, flags) = struct.unpack('<QII', data[:16])
		assert(self.d_off == d_off1)

		collections.OrderedDict.__init__(self)

		for f_off in range(self.d_off + self.ent_len, self.d_off + self.d_len, self.ent_len):
			try:
				entry = Rs5CompressedFileDecoder(f, f.read(self.ent_len))
				self[entry.filename] = entry
			except NotAFile:
				# XXX: Figure out what these are.
				# I think they are just deleted files
				continue

class Rs5ArchiveEncoder(Rs5Archive):
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

	def add_from_buf(self, buf):
		entry = Rs5CompressedFileEncoder(self.fp, buf=buf)
		print "Adding %s..." % entry.filename
		self[entry.filename] = entry

	def add_chunk_dir(self, path):
		print "Adding chunks from %s..." % path
		files = sorted(os.listdir(path))
		files.remove('00-HEADER')
		header = open(os.path.join(path, '00-HEADER'), 'rb')
		header = rs5file.Rs5FileDecoder(header.read())
		chunks = collections.OrderedDict()
		for filename in files:
			chunk_path = os.path.join(path, filename)
			if not os.path.isfile(chunk_path) or '-' not in filename:
				print 'Skipping %s: not a valid chunk' % chunk_path
				continue
			chunk_name = filename.split('-', 1)[1]
			print '  %s' % filename
			chunk = open(chunk_path, 'rb')
			chunk = rs5file.Rs5ChunkEncoder(chunk_name, chunk.read())
			chunks[chunk.name] = chunk
		chunks = rs5file.Rs5ChunkedFileEncoder(header.magic, header.filename, header.u2, chunks)
		entry = Rs5CompressedFileEncoder(self.fp, buf=chunks.encode())
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

	def write_header(self):
		print "Writing RS5 header..."
		self.fp.seek(0)
		self.fp.write(struct.pack('<8sQII', 'CFILEHDR', self.d_off, self.ent_len, self.u1))

	def save(self):
		self._write_directory()
		self.write_header()
		self.fp.flush()
		print "Done."

class Rs5ArchiveUpdater(Rs5ArchiveEncoder, Rs5ArchiveDecoder):
	def __init__(self, fp):
		return Rs5ArchiveDecoder.__init__(self, fp)

	def add(self, filename):
		self.fp.seek(0, 2)
		return Rs5ArchiveEncoder.add(self, filename)

	def add_chunk_dir(self, path):
		self.fp.seek(0, 2)
		return Rs5ArchiveEncoder.add_chunk_dir(self, path)

	def add_from_buf(self, buf):
		self.fp.seek(0, 2)
		return Rs5ArchiveEncoder.add_from_buf(self, buf)

	def save(self):
		self.fp.seek(0, 2)
		self._write_directory()
		# When updating an existing archive we use an extra flush
		# before writing the header to reduce the risk of writing a bad
		# header in case of an IO error, power failure, etc:
		self.fp.flush()
		self.write_header()
		self.fp.flush()
		print "Done."

# vi:noexpandtab:sw=8:ts=8
