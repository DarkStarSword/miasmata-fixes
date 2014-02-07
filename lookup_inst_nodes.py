#!/usr/bin/env python

import sys
import os

import inst_header

def main():
	(x, y) = map(float, sys.argv[1:3])

	# Rotate coord 90 degrees clockwise (transpose then mirror x):
	(x, y) = (inst_header.width - y, x)
	print 'Rotated back to inst coordinates: %d x %d' % (x, y)
	plot_point(x, y, (255, 255, 255), (230, 230, 230))

	for (n, (x1, y1, z1, x2, y2, z2)) in inst_header.get_points():
		assert(x2 > x1)
		assert(y2 > y1)
		if x >= int(x1) and x <= int(x2) and \
		   y >= int(y1) and y <= int(y2):
			c = r = ''
			exists = 64
			if not os.path.exists('nodes/inst_node%d' % n):
				c = '\x1b[31m'
				r = '\x1b[0m'
				exists = 0
			print '%sinst_node%-6d | %8.3f %8.3f %9.3f  x  %8.3f %8.3f %8.3f  |  %4.0f x %-4.0f%s' % \
				   (c, n, x1, y1, z1, x2, y2, z2, x2-x1, y2-y1, r)
			inst_header.plot_node(x1, y1, z1, x2, y2, z2, 128, 128, exists)
	inst_header.save_image('lookup_nodes.png')

if __name__ == '__main__':
	main()

# vi:noexpandtab:sw=8:ts=8
