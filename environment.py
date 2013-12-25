#!/usr/bin/env python

import sys

import data
import rs5file

def assert_chunks(chunks):
	assert(chunks.magic == 'RAW.')
	assert(chunks.filename == 'environment')
	assert(chunks.u2 == 1)
	assert(len(chunks) == 1)

def parse_environment(f, outputfd):
	chunks = rs5file.Rs5ChunkedFileDecoder(f)
	assert_chunks(chunks)

	data.chunk2json(chunks['DATA'], outputfd)

def make_chunks(buf):
	chunk = data.make_chunk(buf)
	chunks = rs5file.Rs5ChunkedFileEncoder('RAW.', 'environment', 1, chunk)
	return chunks.encode()

def json2env(j, outputfd):
	outputfd.write(make_chunks(data.json2data(j)))

def diff_environments(f1, f2):
	chunks1 = rs5file.Rs5ChunkedFileDecoder(f1)
	chunks2 = rs5file.Rs5ChunkedFileDecoder(f2)
	assert_chunks(chunks1)
	assert_chunks(chunks2)
	env1 = data.parse_chunk(chunks1['DATA'])
	env2 = data.parse_chunk(chunks2['DATA'])
	return data.diff_data(env1, env2)

def parse_args():
	import argparse
	parser = argparse.ArgumentParser()

	group = parser.add_mutually_exclusive_group(required=True)
	group.add_argument('-d', '--decode-file', metavar='FILE',
			help='Decode a previously extracted environment file')
	group.add_argument('-e', '--encode-file', metavar='FILE',
			help='Encode a JSON formatted environment file')
	group.add_argument('--diff', nargs=2, metavar='FILE',
			type=argparse.FileType('rb'),
			help='Find the differences between two environment files')

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

	if args.diff:
		return diff_environments(*args.diff)

if __name__ == '__main__':
	main()
