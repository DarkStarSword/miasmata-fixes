#!/usr/bin/env python

import struct
import Image

import rs5file
import miasmap

def parse_inst_header_header(f):
	assert(f.read(6) == '\0\x47\0\0\0\x46')
	(nodes,) = struct.unpack('<I', f.read(4))
	return nodes

def get_points():
	f = open('inst_header')
	filesize = rs5file.parse_raw_header(f)
	nodes = parse_inst_header_header(f)
	for i in range(nodes):
		yield (i, struct.unpack('<6f', f.read(4*6)))

def _get_name_list():
	f = open('inst_header')
	filesize = rs5file.parse_raw_header(f)
	nodes = parse_inst_header_header(f)
	seek = nodes*6*4
	f.seek(seek, 1)
	(num_entries,) = struct.unpack('<I', f.read(4))
	return f.read(filesize - 14 - seek).rstrip('\0').split('\0')

names = None
def get_name_list():
	global names
	if names is None:
		names = _get_name_list()
	return names

def plot_node(x1, y1, z1, x2, y2, z2, r=64, wierd=8, exists=64):
	l1 = int((z1 - minz) * 255.0 / (maxz-minz))
	l2 = int((z2 - minz) * 255.0 / (maxz-minz))

	if z1 == 10000000.0 or z2 == -1000000.0:
		rgb1 = rgb2 = (0, 0, wierd)
	elif exists:
		rgb1 = (exists, l1, 0)
		rgb2 = (exists, l2, 0)
	else:
		rgb1 = (r, 0, 0)
		rgb2 = (r, 0, 0)

	miasmap.plot_rect(int(x1), int(y1), rgb1, int(x2), int(y2), rgb2)
