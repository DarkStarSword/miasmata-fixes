#!/usr/bin/env python

import sys
from PIL import Image, ImageFile
import struct
from StringIO import StringIO
import numpy as np

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

def open_dds(fp, mipmap=None, mode='RGBA'):
	if fp.read(4) != 'DDS ':
		raise ValueError('Not a DDS file')
	header = DDSHeader(fp)

	assert(header.pixel_format.four_cc) in ('DXT5', 'DXT1')
	if header.pixel_format.four_cc == 'DXT1':
		block_size = 8
		fmt = [('c0', '<u2'), ('c1', '<u2'), ('clookup', '<u4')]
	else:
		block_size = 16
		fmt = [('alpha', '<u8'), ('c0', '<u2'), ('c1', '<u2'), ('clookup', '<u4')]

	(width, height) = (header.width, header.height)
	if mipmap:
		while mipmap < (width, height):
			fp.seek(width * height * block_size / 16, 1)
			(width, height) = (width/2, height/2)

	l = width * height / 16 * block_size
	buf = np.frombuffer(fp.read(l), fmt)

	def rgb565(c):
		r = (c & 0xf800) >> 8
		g = (c & 0x07e0) >> 3
		b = (c & 0x001f) << 3
		return np.dstack((r, g, b))

	c = [None]*4
	c[0] = buf['c0'].reshape([height / 4, width / 4])
	c[1] = buf['c1'].reshape([height / 4, width / 4])
	ct = (c[0] <= c[1]).reshape([height / 4, width / 4, 1])
	c[0] = rgb565(c[0])
	c[1] = rgb565(c[1])
	c[2] = np.choose(ct, ((2*c[0] + c[1]) / 3, (c[0] + c[1]) / 2))
	c[3] = np.choose(ct, ((c[0] + 2*c[1]) / 3, np.zeros_like(c[0])))
	del ct
	cl = buf['clookup'].reshape([height / 4, width / 4, 1]).copy()

	alpha = None
	channels = 3
	if header.pixel_format.four_cc == 'DXT5' and mode == 'RGBA':
		channels = 4
		alpha = buf['alpha'].reshape(height / 4, width / 4)
		a = [None]*8
		aa = [None]*8
		ab = [None]*8
		# Byte swapped due to reading in LE
		al = ((alpha & 0xffffffffffff0000) >> 16)
		a[0] = alpha & 0xff
		a[1] = (alpha & 0xff00) >> 8
		at = a[0] <= a[1]
		for i in xrange(1, 7):
			aa[i+1] = ((7-i)*a[0] + i*a[1]) / 7
		for i in xrange(1, 5):
			ab[i+1] = ((5-i)*a[0] + i*a[1]) / 5
		ab[6] = np.zeros_like(a[0])
		ab[7] = np.empty_like(a[0])
		ab[7].fill(255)
		for i in xrange(2, 8):
			a[i] = np.choose(at, [aa[i], ab[i]])
		del aa, ab, at

	out = np.empty([height, width, channels], np.uint16)
	for y in range(4):
		for x in range(4):
			# print y, x

			# I feel like there's probably a more efficient way to do this...

			# Look up the value
			l = np.int32(cl & 0x3)
			cl >>= 2

			# Lookup the value of each of the pixels we are working on:
			o = np.choose(l, c)

			if channels == 4:
				l = np.uint8(al & 0x7)
				al >>= 3

				oa = np.choose(l, a)
				o = np.insert(o, 3, oa, 2)

			# Enlarge that 4x in both directions:
			o = o.repeat(4, 0).repeat(4, 1)

			# Construct a mask of the pixels in the final image we are working on:
			m = np.zeros([4, 4, channels])
			m[y,  x] = [1] * channels
			m = np.tile(m, [height / 4, width / 4, 1])

			# Copy these pixels to the output image - this is the slowest operation:
			np.putmask(out, m, o)

	# Finally cast to uint8 here - too early causes overflows in the DXT
	# calculations and any time after that actually slows things down
	image = Image.fromarray(np.array(out, np.uint8))

	return image

def open_rs5file_imag(file, mipmap=None, mode='RGBA'):
	return open_dds(file['DATA'].get_fp(), mipmap, mode)

if __name__ == '__main__':
	# f = open('main/TEX/Map_FilledIn.dds', 'rb')
	# # image = open_dds(f)
	# # image = open_dds(f, (2048, 2048))
	# image = open_dds(f, (1024, 1024), 'RGB')
	# image.save('test.jpg')

	import rs5archive, rs5file
	print 'Opening main.rs5...'
	archive = rs5archive.Rs5ArchiveDecoder(open('main.rs5', 'rb'))
	print 'Extracting image...'
	file = rs5file.Rs5ChunkedFileDecoder(archive['TEX\\Map_FilledIn'].decompress())
	print 'Decoding image...'
	image = open_rs5file_imag(file, (1024, 1024), 'RGB')
	print 'Saving image...'
	image.save('test.jpg')

# vi:noexpandtab:sw=8:ts=8
