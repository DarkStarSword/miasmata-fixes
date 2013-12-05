#!/usr/bin/env python

import sys
import Image, ImageFile
import struct
import multiprocessing
from StringIO import StringIO

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
		self.pixel_format = DDSPixelFormat(fp)
		(
			self.caps,
			self.caps2,
			self.caps3,
			self.caps4
		) = struct.unpack('<4I4x', fp.read(20))
		assert(size==124)
		assert(self.flags & self.Flags.REQUIRED == self.Flags.REQUIRED)

def dtx1(pix, x, y, c0, c1, clookup):
	def rgb565(c):
		return [(c & 0xf800) >> 8,
			(c & 0x07e0) >> 3,
			(c & 0x001f) << 3]
	table = [ rgb565(c0), rgb565(c1) ]
	z = zip(*table)
	if c0 > c1:
		table.append([ (c0 * 2 + c1) / 3 for (c0, c1) in z ])
		table.append([ (c1 * 2 + c0) / 3 for (c0, c1) in z ])
	else:
		table.append([ (c0     + c1) / 2 for (c0, c1) in z ])
		table.append([0, 0, 0]) # >Transparent< black? Alpha in DTX1?

	for y1 in xrange(y, y+4):
		for x1 in xrange(x, x+4):
			l = clookup & 0x3
			clookup >>= 2
			pix[x1, y1] = tuple(table[l])

def dtx5(pix, x, y, alpha):
	# Byte swapped due to reading in LE
	a0      = (alpha & 0x00000000000000ff) >> 0
	a1      = (alpha & 0x000000000000ff00) >> 8
	alookup = (alpha & 0xffffffffffff0000) >> 16

	table = [a0, a1]

	if a0 > a1:
		for i in xrange(1, 7):
			table.append(((7-i)*a0 + i*a1) / 7)
	else:
		for i in xrange(1, 5):
			table.append(((5-i)*a0 + i*a1) / 5)
		table.append(0)
		table.append(255)

	for y1 in xrange(y, y+4):
		for x1 in xrange(x, x+4):
			l = alookup & 0x7
			alookup >>= 3
			pix[x1, y1] = pix[x1, y1][0:3] + (table[l],)

def process_strip((y, mode, buf)):
	width = len(buf) / 4
	buf = StringIO(buf)
	image = Image.new(mode, (width, 4))
	pix = image.load()
	for x in xrange(0, width, 4):
		(alpha, c0, c1, clookup) = struct.unpack('<QHHI', buf.read(16))
		dtx1(pix, x, 0, c0, c1, clookup)
		if mode == 'RGBA':
			dtx5(pix, x, 0, alpha)
	return (y, image.tostring())

def open_dds(fp, mipmap=None, mode='RGBA'):
	if fp.read(4) != 'DDS ':
		raise ValueError('Not a DDS file')
	header = DDSHeader(fp)
	assert(header.pixel_format.four_cc) == 'DXT5'

	(width, height) = (header.width, header.height)
	if mipmap:
		while mipmap < (width, height):
			fp.seek(width * height, 1)
			(width, height) = (width/2, height/2)

	buf = [ (y, mode, fp.read(16 * width / 4)) for y in xrange(0, height, 4) ]

	image = Image.new(mode, (width, height))
	pix = image.load()

	pool = multiprocessing.Pool()

	for (y, strip) in pool.imap_unordered(process_strip, buf, height / 16):
		image.paste(Image.fromstring(mode, (width, 4), strip), (0, y))

	return image


if __name__ == '__main__':
	f = open('main/TEX/Map_FilledIn.dds', 'rb')
	# image = open_dds(f)
	# image = open_dds(f, (2048, 2048))
	image = open_dds(f, (1024, 1024), 'RGB')
	image.save('test.jpg')
