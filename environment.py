#!/usr/bin/env python

import sys

import data
import rs5

def parse_environment(f, outputfd):
	(magic, filename, filesize, u2) = rs5.parse_rs5file_header(f)
	assert(magic == 'RAW.')
	assert(filename == 'environment')
	assert(u2 == 1)

	data.parse_wrapped_data(f, outputfd)

def json2env(j, outputfd):
	d = data.wrap_data(data.json2data(j))
	outputfd.write(rs5.enc_file('RAW.', 'environment', d, 1))

def parse_args():
	import argparse
	parser = argparse.ArgumentParser()

	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('-d', '--decode-file', metavar='FILE',
			help='Decode a previously extracted environment file')
	group.add_argument('-e', '--encode-file', metavar='FILE',
			help='Encode a JSON formatted environment file')

	parser.add_argument('-o', '--output',
			type=argparse.FileType('wb'), default=sys.stdout,
			help='Store the result in OUTPUT')

	return parser.parse_args()

def main():
	args = parse_args()

	if args.decode_file:
		return parse_environment(open(args.decode_file, 'rb'), args.output)

	if args.encode_file:
		return json2env(open(args.encode_file, 'rb'), args.output)

if __name__ == '__main__':
	main()
