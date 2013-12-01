#!/usr/bin/env python

import sys
import Image, ImageFile
import struct
from StringIO import StringIO

class DDSImageFile(ImageFile.ImageFile):
	format = format_description = "DDS"

	# Documentation:
	# https://en.wikipedia.org/wiki/S3_Texture_Compression
	# http://msdn.microsoft.com/en-us/library/windows/desktop/bb943991(v=vs.85).aspx

	class DDSPixelFormat(object):
		# http://msdn.microsoft.com/en-us/library/windows/desktop/bb943984(v=vs.85).aspx
		class Flags(object):
			ALPHAPIXELS = 0x00001
			ALPHA       = 0x00002
			FOURCC      = 0x00004
			RGB         = 0x00040
			YUV         = 0x00200
			LUMINANCE   = 0x20000

		def __init__(self, fp):
			(
				size,
				self.flags,
				four_cc,
				rgb_bit_count,
				r_bit_mask,
				g_bit_mask,
				b_bit_mask,
				a_bit_mask
			) = struct.unpack('<2I 4s 5I', fp.read(32))

			assert(size == 32)
			if self.flags & self.Flags.ALPHAPIXELS: # uncompressed
				self.a_bit_mask = a_bit_mask
			assert(not self.flags & self.Flags.ALPHA) # old file
			if self.flags & self.Flags.FOURCC:
				self.four_cc = four_cc
			if self.flags & self.Flags.RGB: # uncompressed
				self.rgb_bit_count = rgb_bit_count
				self.r_bit_mask = r_bit_mask
				self.g_bit_mask = g_bit_mask
				self.b_bit_mask = b_bit_mask
			assert(not self.flags & self.Flags.YUV) # old file
			assert(not self.flags & self.Flags.LUMINANCE) # old file


	class DDSHeader(object):
		# http://msdn.microsoft.com/en-us/library/windows/desktop/bb943982(v=vs.85).aspx
		class Flags(object):
			# Note: Don't rely on these flags - not all writers set them
			CAPS        = 0x000001
			HEIGHT      = 0x000002
			WIDTH       = 0x000004
			PITCH       = 0x000008
			PIXELFORMAT = 0x001000
			MIPMAPCOUNT = 0x020000
			LINEARSIZE  = 0x080000
			DEPTH       = 0x800000
			REQUIRED = CAPS | HEIGHT | WIDTH | PIXELFORMAT

		def __init__(self, fp):
			(
				size,
				self.flags,
				self.height,
				self.width,
				self.pitch_or_linear_size,
				self.depth,
				self.mip_map_count
			) = struct.unpack('<7I 44x', fp.read(72))
			self.pixel_format = DDSImageFile.DDSPixelFormat(fp)
			(
				self.caps,
				self.caps2,
				self.caps3,
				self.caps4
			) = struct.unpack('<4I4x', fp.read(20))
			assert(size==124)
			assert(self.flags & self.Flags.REQUIRED == self.Flags.REQUIRED)

	def _open(self):
		if self.fp.read(4) != 'DDS ':
			raise SyntaxError('Not a DDS file')
		self.header = DDSImageFile.DDSHeader(self.fp)
		assert(self.fp.tell() == 128)
		assert(self.header.pixel_format.four_cc) == 'DXT5'

		self.size = (self.header.width, self.header.height)

		if self.header.pixel_format.four_cc == 'DXT1':
			self.mode = 'RGB'
		else:
			self.mode = 'RGBA'

		self.tile = []
		for y in range(0, self.header.height, 4):
			# for x in range(0, self.header.width, 4):
			# 	self.tile.append((
			# 		('raw', (x, y, x+4, y+4),
			# 			0x80 + (y*self.header.width + x) / 4 * 128,
			# 			(self.mode, 0, 1))
			# 	))
			self.tile.append((
				('raw', (0, y, self.header.width, y+4),
					0x80 + (y*self.header.width),
					('RGBA', 0, 1))
			))
		print len(self.tile)

	@staticmethod
	def _dtx1(c0, c1, clookup):
		def rgb565(c):
			return [(c & 0xf800) >> 8,
			        (c & 0x07e0) >> 3,
			        (c & 0x001f) << 3]
		rgbs = ( rgb565(c0), rgb565(c1) )
		table = [ struct.pack('3B', *c) for c in rgbs ]
		z = zip(*rgbs)
		if c0 > c1:
			table.append(struct.pack('3B', *[ (c0 * 2 + c1) / 3 for (c0, c1) in z ]))
			table.append(struct.pack('3B', *[ (c1 * 2 + c0) / 3 for (c0, c1) in z ]))
		else:
			table.append(struct.pack('3B', *[ (c0     + c1) / 2 for (c0, c1) in z ]))
			table.append('\0\0\0') # >Transparent< black? Alpha in DTX1?

		ret = []
		for y in range(4):
			row = []
			for x in range(4):
				shift = (y * 4 + x) * 2
				l = (clookup >> shift) & 0x3;
				row.append(table[l])
			ret.append(row)
		return ret

	def dtx1(self):
		return self._dtx1(*struct.unpack('<HHI'))

	@staticmethod
	def _dtx45_alpha(alpha):
		# Byte swapped due to reading in LE
		a0      = (alpha & 0x00000000000000ff) >> 0
		a1      = (alpha & 0x000000000000ff00) >> 8
		alookup = (alpha & 0xffffffffffff0000) >> 16

		table = [chr(a0), chr(a1)]

		if a0 > a1:
			for i in range(1, 7):
				table.append(chr(((7-i)*a0 + i*a1) / 7))
		else:
			for i in range(1, 5):
				table.append(chr(((5-i)*a0 + i*a1) / 5))
			table.append('\0')
			table.append('\xff')

		ret = []
		for y in range(4):
			row = []
			for x in range(4):
				shift = (y * 4 + x) * 3
				l = (alookup >> shift) & 0x7
				row.append(table[l])
			ret.append(row)
		return ret

	def dtx5(self):
		(alpha, c0, c1, clookup) = struct.unpack('<QHHI', self.fp.read(16))
		ret = self._dtx1(c0, c1, clookup)
		aret = self._dtx45_alpha(alpha)
		for y in range(4):
			ret[y] = [ c+a for (c,a) in zip(ret[y], aret[y]) ]
		return ret

	i=0
	def load_read(self, size):
		print>>sys.stderr, self.i
		self.i+=1
		ret = [[], [], [], []]
		for x in range(0, self.header.width, 4):
			r = self.dtx5()
			for y in range(4):
				ret[y].extend(r[y])

		return ''.join( [ ''.join(y) for y in ret ] )



Image.register_open('DDS', DDSImageFile)
Image.register_extension('DDS', '.dds')
