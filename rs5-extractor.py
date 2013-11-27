#!/usr/bin/env python

# Based loosely on git://github.com/klightspeed/RS5-Extractor

# I wanted something a bit lower level that didn't convert the contained files
# so I could examine the format for myself. Don't expect this to be feature
# complete and a re-packer is probably a long way off.

import struct
import zlib
import sys
import os

def win_time(win_time):
	# http://msdn.microsoft.com/en-us/library/system.datetime.fromfiletimeutc.aspx:
	# A Windows file time is a 64-bit value that represents the number of
	# 100-nanosecond intervals that have elapsed since 12:00 midnight,
	# January 1, 1601 A.D. (C.E.) Coordinated Universal Time (UTC).
	import time, calendar
	win_epoch = calendar.timegm((1601, 1, 1, 0, 0, 0))
	return(win_time / 10000000 + win_epoch)

def mkdir_recursive(path):
	if path == '':
		return
	(head, tail) = os.path.split(path)
	mkdir_recursive(head)
	if not os.path.exists(path):
		os.mkdir(path)
	elif not os.path.isdir(path):
		raise OSError(17, '%s exists but is not a directory' % path)

class rs5ent(object):
	def __init__(self, f, data):
		self.fp = f
		(self.data_off, self.data_len, unknown1, self.type, unknown2,
				modtime) \
			= struct.unpack('<QIQ4sQQ', data[:40])
		filename_len = data[40:].find('\0')
		self.filename = data[40:40 + filename_len].replace('\\', os.path.sep)
		self.modtime = win_time(modtime)
		# print repr(self.type), self.filename
		# print hex(self.data_off), hex(self.data_len)

		# print hex(unknown1), hex(unknown2)
		# # assert(unknown1 == 0x30080000000)
		# if unknown1 != 0x30080000000:
		# 	print repr(self.type), self.filename
		# 	print hex(unknown1), hex(unknown2)

	def extract(self, base_path):
		dest = os.path.join(base_path, self.filename)
		if os.path.isfile(dest): # and size != 0
			print>>sys.stderr, 'Skipping %s - file exists.' % dest
			return
		(dir, file) = os.path.split(dest)
		mkdir_recursive(dir)
		f = open(dest, 'wb')
		self.fp.seek(self.data_off)
		data = self.fp.read(self.data_len)
		try:
			f.write(zlib.decompress(data))
		except zlib.error, e:
			print>>sys.stderr, 'ERROR EXTRACTING %s: %s. Skipping decompression!' % (dest, str(e))
			f.write(data)
		f.close()


class rs5dir(list):
	def __init__(self, f, d_off, ent_len):
		f.seek(d_off)
		data = f.read(ent_len)
		(d_off1, d_len, flags) = struct.unpack('<QII', data[:16])
		assert(d_off == d_off1)
		# print hex(d_len), hex(flags)

		list.__init__(self)

		for f_off in range(d_off + ent_len, d_off + d_len, ent_len):
			# print hex(f_off)
			self.append(rs5ent(f, f.read(ent_len)))

class rs5file(rs5dir):
	def __init__(self, f):
		magic = f.read(8)
		if magic != 'CFILEHDR':
			print 'Invalid file header'
			return 1

		(d_off, ent_len) = struct.unpack('<QI', f.read(12))
		# print hex(d_off), hex(ent_len)

		# What is the data following this header?

		rs5dir.__init__(self, f, d_off, ent_len)

def main():
	filename = sys.argv[1]
	root = rs5file(open(filename, 'rb'))
	dest = os.path.split(filename)
	dest = os.path.join(dest[0], 'EXTRACTED-' + dest[1])
	print 'Extracting files to %s' % dest
	for file in root:
		if not file.filename:
			print 'SKIPPING FILE OF TYPE %s WITHOUT FILENAME' % repr(file.type)
			continue
		print 'Extracting %s %s...' % (repr(file.type), file.filename)
		try:
			file.extract(dest)
		except OSError, e:
			print>>sys.stderr, 'ERROR EXTRACTING %s: %s, SKIPPING!' % (file.filename, str(e))

if __name__ == '__main__':
	sys.exit(main())
