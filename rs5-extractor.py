#!/usr/bin/env python

import zlib
import sys
import os
import rs5archive
import rs5file

def list_files(archive, file_list, list_chunks=False):
	rs5 = rs5archive.Rs5ArchiveDecoder(open(archive, 'rb'))
	if not file_list:
		file_list = rs5
	for filename in file_list:
		filename = filename.replace(os.path.sep, '\\')
		try:
			file = rs5[filename]
		except KeyError:
			print '%s not found in %s~' % (filename, archive)
			continue
		print '%4s %8i %s' % (file.type, file.uncompressed_size, file.filename)
		if list_chunks and file.type not in ('PROF', 'INOD', 'FOGN'):
			chunks = rs5file.rs5_file_decoder_factory(file.decompress())
			if not hasattr(chunks, 'itervalues'):
				continue
			for chunk in chunks.itervalues():
				print '%4s %8s - %4s %8i' % ('', '', chunk.name, chunk.size)
			print

def extract(archive, dest, file_list, strip, chunks, overwrite, filter):
	rs5 = rs5archive.Rs5ArchiveDecoder(open(archive, 'rb'))
	print 'Extracting files to %s' % dest
	if not file_list:
		file_list = rs5
	for filename in file_list:
		filename = filename.replace(os.path.sep, '\\')
		if filename not in rs5:
			print '%s not found in %s!' % (filename, archive)
			continue
		type = rs5[filename].type
		if filter and type not in filter:
			continue
		try:
			print 'Extracting %s %s...' % (repr(type), filename)
			if chunks:
			    rs5[filename].extract_chunks(dest, overwrite)
			else:
			    rs5[filename].extract(dest, strip, overwrite)
		except OSError as e:
			print>>sys.stderr, 'ERROR EXTRACTING %s: %s, SKIPPING!' % (file.filename, str(e))

def is_chunk_dir(path):
	return os.path.isfile(os.path.join(path, '00-HEADER'))

def create_rs5(archive, file_list, overwrite):
	if not file_list:
		print 'Must specify at least one file!'
		return
	if os.path.exists(archive) and not overwrite:
		print '%s already exists, refusing to continue!' % archive
		return
	rs5 = rs5archive.Rs5ArchiveEncoder(archive)

	for filename in file_list:
		if os.path.isdir(filename):
			if is_chunk_dir(filename):
				rs5.add_chunk_dir(filename)
				continue
			for (root, dirs, files) in os.walk(filename):
				for dir in dirs[:]:
					path = os.path.join(root, dir)
					if is_chunk_dir(path):
						rs5.add_chunk_dir(path)
						dirs.remove(dir)
				for file in files:
					rs5.add(os.path.join(root, file))
		else:
			rs5.add(filename)

	rs5.save()

def add_rs5_files(archive, file_list):
	rs5 = rs5archive.Rs5ArchiveUpdater(open(archive, 'rb+'))
	for filename in file_list:
		if is_chunk_dir(filename):
			rs5.add_chunk_dir(filename)
		else:
			rs5.add(filename)
	rs5.save()

def repack_rs5(old_archive, new_archive):
	old_rs5 = rs5archive.Rs5ArchiveDecoder(open(old_archive, 'rb'))
	new_rs5 = rs5archive.Rs5ArchiveEncoder(new_archive)
	for old_file in old_rs5.itervalues():
		print 'Repacking %s...' % old_file.filename
		new_entry = rs5archive.Rs5CompressedFileRepacker(new_rs5.fp, old_file)
		new_rs5[new_entry.filename] = new_entry
	new_rs5.save()


def analyse(filename):
	rs5 = rs5archive.Rs5ArchiveDecoder(open(filename, 'rb'))
	interesting = ('cterr_texturelist',)
	for file in rs5.itervalues():
		if not file.filename:
			# XXX: What are these?
			# print 'SKIPPING FILE OF TYPE %s WITHOUT FILENAME' % repr(file.type)
			continue
		try:
			d = file.decompress()
			size = len(d)
		except zlib.error as e:
			# XXX: What are these?
			print 'ERROR EXTRACTING %s: %s' % (file.filename, str(e))
			print '%s %x %8i %x    |   %-25s  |  compressed_size: %i' \
				% (file.type, file.u1, file.uncompressed_size, file.u2, file.filename, file.compressed_size)
			if file.filename in interesting:
				continue
			raise
			# continue
		contents = rs5file.rs5_file_decoder_factory(d)
		# if file.filename in interesting:
		if True:
			print '0x%.8x - 0x%.8x  |  %s %x %8i %x %x  |   %-25s  |  compressed_size: %i\t|  size: %8i' \
				% (file.data_off, file.data_off + file.compressed_size-1, file.type, file.u1, file.uncompressed_size, file.u2, contents.u2, file.filename, file.compressed_size, contents.filesize+contents.data_off)

		assert(file.u2 == 1)
		assert(file.uncompressed_size == size)
		assert(file.type == contents.magic)
		assert(file.filename == contents.filename)

		# ALIGNMENT CONSTRAINT FOUND - FILE IS PADDED TO 8 BYTES BEFORE COMPRESSION
		assert(file.uncompressed_size % 8 == 0)

		# PADDING CONSTRAINT - FILE HEADER IS PADDED TO A MULTIPLE OF 8 BYTES
		assert(contents.data_off % 8 == 0)

		# NO PADDING CONSTRAINTS FOUND ON CONTAINED FILES IN THE GENERAL CASE
		# assert(contents.filesize % 2 == 0)
		# assert(contents.filesize % 4 == 0)
		# assert(contents.filesize % 8 == 0)
		#assert((contents.data_off + contents.filesize) % 2 == 0)
		#assert((contents.data_off + contents.filesize) % 4 == 0)
		#assert((contents.data_off + contents.filesize) % 8 == 0)
		#assert((contents.data_off + contents.filesize) % 16 == 0)

def parse_args():
	import argparse
	parser = argparse.ArgumentParser()

	group = parser.add_mutually_exclusive_group(required=True)
	parser.add_argument('files', nargs='*', metavar='FILE')
	group.add_argument('-l', '--list', action='store_true',
			help='List all files in the rs5 archive')
	group.add_argument('-L', '--list-chunks', action='store_true',
			help='List all files and contained chunks in the rs5 archive')
	group.add_argument('-x', '--extract', action='store_true',
			help='Extract files from the archive')
	group.add_argument('-c', '--create', action='store_true',
			help='Create a new RS5 file')
	group.add_argument('-a', '--add', action='store_true',
			help='Add/update FILEs in ARCHIVE')
	group.add_argument('--repack', metavar='NEW_ARCHIVE',
			help='Decode ARCHIVE and pack into NEW_ARCHIVE, for testing')

	parser.add_argument('-f', '--file', metavar='ARCHIVE', required=True,
			help='Specify the rs5 ARCHIVE to work on')
	parser.add_argument('-C', '--directory', metavar='DIR',
			help='Change to directory DIR before extacting')

	group1 = parser.add_mutually_exclusive_group()
	group1.add_argument('--strip', action='store_true',
			help='Strip the local file headers during extraction')
	group1.add_argument('--chunks', action='store_true',
			help='Split files up into their component chunks while extracting')
	parser.add_argument('--filter', action='append',
			help='Only extract files of this type')

	parser.add_argument('--overwrite', action='store_true',
			help='Overwrite files without asking')

	group.add_argument('--analyse', action='store_true')

	return parser.parse_args()

def main():
	args = parse_args()

	if args.list:
		return list_files(args.file, args.files)

	if args.list_chunks:
		return list_files(args.file, args.files, list_chunks=True)

	if args.extract:
		directory = args.directory
		if directory is None:
			directory = os.path.splitext(os.path.basename(args.file))[0]
			if directory == args.file:
				print 'Unable to determine target directory'
				return
		return extract(args.file, directory, args.files, args.strip, args.chunks, args.overwrite, args.filter)

	if args.create:
		return create_rs5(args.file, args.files, args.overwrite)

	if args.add:
		return add_rs5_files(args.file, args.files)

	if args.repack is not None:
		return repack_rs5(args.file, args.repack)

	if args.analyse:
		return analyse(args.file)

if __name__ == '__main__':
	sys.exit(main())

# vi:noexpandtab:sw=8:ts=8
