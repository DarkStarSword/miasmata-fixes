#!/usr/bin/env python

import sys
import os

import inst_header

def main():
	nodes = open('inst_list', 'r').readlines()
	nodes = set([ int(x[9:-1]) for x in nodes ])
	for (n, (x1, y1, z1, x2, y2, z2)) in inst_header.get_points():
		if n % 10000 == 0:
			print n, '...'

		#def fmt_flt(f):
		#	return '%f' % f
		#print '\t'.join(map(fmt_flt, (x, y, z)))

		# if z1 == 10000000.0 or z2 == -1000000.0:
		# 	assert(not os.path.exists('nodes/inst_node%d' % n))

		#if not os.path.exists('nodes/inst_node%d' % n):
		#	continue
		if not n in nodes:
			continue

		inst_header.plot_node(x1, y1, z1, x2, y2, z2)

	inst_header.save_image('all_nodes_exists.jpg')

if __name__ == '__main__':
	main()
