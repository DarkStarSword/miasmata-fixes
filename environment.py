#!/usr/bin/env python

import sys

import data
import rs5file

def parse_environment(f, outputfd):
	chunks = rs5file.Rs5ChunkedFileDecoder(f)
	assert(chunks.magic == 'RAW.')
	assert(chunks.filename == 'environment')
	assert(chunks.u2 == 1)
	assert(len(chunks) == 1)

	data.chunk2json(chunks['DATA'], outputfd)

def make_chunks(buf):
	chunk = data.make_chunk(buf)
	chunks = rs5file.Rs5ChunkedFileEncoder('RAW.', 'environment', 1, chunk)
	return chunks.encode()

def json2env(j, outputfd):
	outputfd.write(make_chunks(data.json2data(j)))

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
