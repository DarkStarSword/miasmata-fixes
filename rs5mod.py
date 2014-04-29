#!/usr/bin/env python

import sys
import os
import rs5archive
import rs5file

undo_file = r'MIASMOD\UNDO'
mod_manifests = r'MIASMOD\MODS'
mod_order_file = r'MIASMOD\ORDER'
mod_meta_file = r'MIASMOD\MODINFO'

def file_blacklisted(name):
	'''Files not permitted to be manually added to an archive'''
	if name.upper() in (undo_file, mod_order_file):
		return True
	if name.upper().startswith('%s\\' % mod_manifests):
		return True
	return False

def validate_undo(rs5):
	print 'STUB: validate_undo()'
	# TODO: Make sure the values in the undo file look sane - that there is
	# a central directory archive where it points and that there is no file
	# listed in that directory past the truncation point.
	return True

class UndoMeta(dict):
	import json

	def revert_rs5(self, rs5):
		# TODO: Validate undo
		rs5.d_off = self['directory_offset']
		rs5.ent_len = self['entry_size']
		rs5.write_header()
		rs5.fp.flush()
		rs5.fp.truncate(self['filesize'])

class UndoMetaEncoder(UndoMeta, rs5file.Rs5FileEncoder):
	def __init__(self, rs5):
		self['filesize'] = os.fstat(rs5.fp.fileno()).st_size
		self['directory_offset'] = rs5.d_off
		self['entry_size'] = rs5.ent_len
		self['directory_size'] = rs5.d_orig_len
		rs5file.Rs5FileEncoder.__init__(self, 'META', undo_file, self.json.dumps(self), 0)

class UndoMetaDecoder(UndoMeta, rs5file.Rs5FileDecoder):
	def __init__(self, rs5):
		rs5file.Rs5FileDecoder.__init__(self, rs5[undo_file].decompress())
		self.update(self.json.loads(self.data))

def do_add_undo(rs5, overwrite=False):
	if undo_file in rs5 and not overwrite:
		print 'Previously added undo metadata found'
		if validate_undo(rs5):
			return 1
		print 'Undo metadata appears to be invalid, updating'
	undo = UndoMetaEncoder(rs5)
	try:
		rs5.add_from_buf(undo.encode())
		rs5.save()
	except Exception as e:
		print>>sys.stderr, 'ERROR: %s occured while adding undo metadata: %s' % (e.__class__.__name__, str(e))
		print>>sys.stderr, 'REVERTING CHANGES...'
		undo.revert_rs5(rs5)
		print>>sys.stderr, '\nFILE RESTORED'
		raise

def add_undo(archive, overwrite):
	rs5 = rs5archive.Rs5ArchiveUpdater(open(archive, 'rb+'))
	try:
		return do_add_undo(rs5, overwrite)
	except Exception as e:
		return 1

def revert(archive):
	rs5 = rs5archive.Rs5ArchiveUpdater(open(archive, 'rb+'))
	if undo_file not in rs5:
		print '%s does not contain undo metadata!' % archive
		return 1
	if not validate_undo(rs5):
		print 'Undo metadata appears to be invalid, aborting!'
		return 1
	undo = UndoMetaDecoder(rs5)
	undo.revert_rs5(rs5)

class ModCentralDirectoryEncoder(rs5archive.Rs5CentralDirectoryEncoder, rs5file.Rs5FileEncoder):
	def __init__(self, name, ent_len):
		self.ent_len = ent_len
		self.flags = 0
		rs5archive.Rs5CentralDirectoryEncoder.__init__(self)
		self.filename = '%s\%s.manifest' % (mod_manifests, name)

	def encode(self):
		from StringIO import StringIO
		self.fp = StringIO()
		self.write_directory()
		rs5file.Rs5FileEncoder.__init__(self, 'META', self.filename, self.fp.getvalue(), 0)
		return rs5file.Rs5FileEncoder.encode(self)

class UndoMetaCentralDirectory(rs5archive.Rs5CentralDirectoryDecoder):
	def __init__(self, rs5):
		undo = UndoMetaDecoder(rs5)
		self.fp = rs5.fp
		self.d_off = undo['directory_offset']
		self.ent_len = undo['entry_size']
		rs5archive.Rs5CentralDirectoryDecoder.__init__(self)

class ModCentralDirectoryDecoder(rs5archive.Rs5CentralDirectoryDecoder):
	def __init__(self, rs5, manifest):
		from StringIO import StringIO
		decoder = rs5file.Rs5FileDecoder(manifest.decompress())
		self.fp = StringIO(decoder.data)
		self.d_off = 0
		self.ent_len = rs5.ent_len
		rs5archive.Rs5CentralDirectoryDecoder.__init__(self)

class ModOrder(list):
	import json

class ModOrderEncoder(ModOrder, rs5file.Rs5FileEncoder):
	def __init__(self, rs5, order):
		list.__init__(self, order)
		rs5file.Rs5FileEncoder.__init__(self, 'META', mod_order_file, self.json.dumps(self), 0)

class ModOrderDecoder(ModOrder, rs5file.Rs5FileDecoder):
	def __init__(self, rs5):
		rs5file.Rs5FileDecoder.__init__(self, rs5[mod_order_file].decompress())
		list.__init__(self, self.json.loads(self.data))

def rs5_mods(rs5):
	mods = filter(lambda x: x.startswith('%s\\' % mod_manifests) and x.endswith('.manifest'), rs5)
	if mod_order_file in rs5:
		order = ModOrderDecoder(rs5)
		for mod in order:
			manifest = '%s\\%s.manifest' % (mod_manifests, mod)
			if manifest in rs5:
				# print 'Processing %s (ordered)' % mod
				yield mods.pop(mods.index(manifest))
			else:
				print 'WARNING: %s listed in %s not found in archive!' % (mod, mod_order_file)
	for mod in mods:
		# print 'Processing %s (UNORDERED)' % mod
		yield mod

def iter_all_file_versions(rs5, undo):
	'''
	Iterates over every file in the archive, including multiple versions of
	the same file where a mod has overridden them.
	'''
	done = set()

	if undo is not None:
		mods = list(rs5_mods(rs5))
		masked = {}
		for mod_name in mods:
			mod = ModCentralDirectoryDecoder(rs5, rs5[mod_name])
			masked.update(zip(mod, [mod_name] * len(mod)))

		def process(file, mod=None):
			done.add((file.filename, file.data_off))
			mask = None
			if file.filename in masked:
				mask = masked[file.filename]
				if mask == mod:
					mask = None
			return (file, mod, mask)

		yield process(rs5[undo_file])
		for file in UndoMetaCentralDirectory(rs5).itervalues():
			yield process(file)
		for mod in mods:
			yield process(rs5[mod], mod)
			for file in ModCentralDirectoryDecoder(rs5, rs5[mod]).itervalues():
				yield process(file, mod)

	for (filename, off) in set([(x.filename, x.data_off) for x in rs5.values()]).difference(done):
		yield (rs5[filename], None, None)

def iter_mod_file_versions(rs5, undo_pos):
	'''
	Iterates over every file in the archive that has been added via a mod
	or manually since undo information was added, including multiple
	versions of the same file where multiple mods have touched the same file.
	'''
	done = set()
	def process(file):
		assert(file.data_off >= undo_pos)
		done.add((file.filename, file.data_off))
		return file

	for mod in rs5_mods(rs5):
		yield process(rs5[mod])
		for file in ModCentralDirectoryDecoder(rs5, rs5[mod]).itervalues():
			yield process(file)

	remaining = set([(x.filename, x.data_off) for x in rs5.values()]).difference(done)
	remaining = filter(lambda (filename, off): off >= undo_pos, remaining)
	for (filename, off) in remaining:
		yield rs5[filename]

def iter_all_used_sections(rs5):
	try:
		undo = UndoMetaDecoder(rs5)
	except KeyError:
		undo = None
	yield (0, 24, '<HEADER>', None, None) # Header
	yield (rs5.d_off, rs5.d_off + rs5.d_orig_len, '<CENTRAL DIRECTORY>', None, None) # Central Directory
	if undo is not None and (undo['directory_offset'] != rs5.d_off or undo['directory_size'] != rs5.d_orig_len):
		yield (undo['directory_offset'], undo['directory_offset'] + undo['directory_size'], '<ORIGINAL CENTRAL DIRECTORY>', None, 'other central directory')
	for (file, mod, masked) in iter_all_file_versions(rs5, undo):
		yield (file.data_off, file.data_off + file.compressed_size, file.filename, mod, masked)

def iter_used_sections(rs5):
	undo = rs5[undo_file]
	undo_pos = undo.data_off + undo.compressed_size

	yield (0, undo_pos, '__original__')
	if rs5.d_off >= undo_pos:
		yield (rs5.d_off, rs5.d_off + rs5.d_orig_len, '__directory__') # Central Directory
	for file in iter_mod_file_versions(rs5, undo_pos):
		yield (file.data_off, file.data_off + file.compressed_size, file.filename)

def find_eof(rs5):
	'''
	Finds the end of the rs5 archive, ensuring that it is past the undo
	metadata, central directory and any installed mods. The archive should
	be safe to truncate at this point.
	'''
	return max([x[1] for x in iter_used_sections(rs5)])

def list_holes(archive):
	rs5 = rs5archive.Rs5ArchiveDecoder(open(archive, 'rb'))
	regions = sorted(iter_all_used_sections(rs5))
	wasted = 0
	bad = False
	for (i, (start, fin, name, mod, masked)) in enumerate(regions):
		if i:
			space = start - regions[i-1][1]
			if space:
				print '<-- HOLE: %i bytes -->' % space
				wasted += space
			if space < 0:
				print ' !!! WARNING: %i BYTES OF OVERLAPPING DATA DETECTED !!!' % -space
				bad = True
		mask_str = mod_str = ''
		if mod is not None:
			mod_str = '(%s) ' % mod
		if masked is not None:
			mask_str = ' (MASKED BY %s)' % masked
		print '%.8x:%.8x %s%s%s' % (start, fin, mod_str, name, mask_str)
	print
	print 'Total space wasted by holes: %i bytes' % wasted
	assert (not bad)

def find_holes(rs5):
	undo = rs5[undo_file]
	undo_pos = undo.data_off + undo.compressed_size
	regions = sorted(iter_used_sections(rs5))
	holes = []
	for (i, (start, fin, name)) in enumerate(regions[:-1]):
		assert (fin >= undo_pos)
		space = regions[i+1][0] - fin
		assert(space >= 0)
		if space > 0:
			holes.append((space, fin))
	return holes

class Rs5ModArchiveUpdater(rs5archive.Rs5ArchiveUpdater):
	def __init__(self, fp):
		rs5archive.Rs5ArchiveUpdater.__init__(self, fp)
		self.holes = None

	def __delitem__(self, item):
		rs5archive.Rs5ArchiveUpdater.__delitem__(self, item)
		self.holes = None

	def find_holes(self):
		print 'Searching for holes...'
		self.holes = sorted(find_holes(self))
		if len(self.holes):
			print '\n'.join('Hole found: %i bytes at 0x%x' % x for x in self.holes)
		else:
			print 'No holes found'

	def seek_find_hole(self, size):
		if undo_file not in self:
			return self.seek_eof()
		if self.holes is None:
			self.find_holes()
		for (i, (hole_size, hole)) in enumerate(self.holes):
			if hole_size >= size:
				print 'Filling hole at 0x%x of size %i with %i bytes' % (hole, hole_size, size)
				if hole_size == size:
					del self.holes[i]
				else:
					self.holes[i] = (hole_size - size, hole + size)
					self.holes.sort() # Insertion sort would be more efficient here
				return self.fp.seek(hole)

		return self.seek_eof()

	def truncate_eof(self):
		self.holes = None
		self.fp.truncate(find_eof(self))

def apply_mod_order(rs5):
	'''
	Rebuild the central directory from the original and any contained mod
	manifests to ensure that files touched by multiple mods use the correct
	one.
	'''
	directory = UndoMetaCentralDirectory(rs5)
	for mod in rs5_mods(rs5):
		directory.update(ModCentralDirectoryDecoder(rs5, rs5[mod]))

	rs5.update(directory)

def order_mods(archive, mod_list):
	rs5 = Rs5ModArchiveUpdater(open(archive, 'rb+'))
	do_add_undo(rs5)
	file = ModOrderEncoder(rs5, mod_list)
	rs5.add_from_buf(file.encode())
	apply_mod_order(rs5)
	rs5.save()
	rs5.truncate_eof()

class ModNotFound(Exception): pass

def do_rm_mod(rs5, mod):
	manifest_name = '%s\\%s.manifest' % (mod_manifests, mod)
	modinfo_name = '%s\\%s.modinfo' % (mod_manifests, mod)
	try:
		manifest = rs5[manifest_name]
	except:
		print 'ERROR: %s not found in archive!' % manifest_name
		raise ModNotFound()
	for (filename, mod_f) in ModCentralDirectoryDecoder(rs5, manifest).iteritems():
		cur_f = rs5[filename]
		if cur_f.data_off == mod_f.data_off:
			print 'Removing %s...' % filename
			del rs5[filename]
		else:
			print 'Skipping %s - offsets do not match' % filename
	print 'Removing %s...' % manifest_name
	del rs5[manifest_name]
	if modinfo_name in rs5:
		del rs5[modinfo_name]
	print 'Rebuilding directory from mod order...'
	apply_mod_order(rs5)
	rs5.save()
	rs5.truncate_eof()

def rm_mod(archive, mods):
	rs5 = Rs5ModArchiveUpdater(open(archive, 'rb+'))
	do_add_undo(rs5)
	for mod in mods:
		try:
			do_rm_mod(rs5, mod)
		except ModNotFound:
			return 1

def get_mod_meta(rs5):
	return rs5file.Rs5ChunkedFileDecoder(rs5[mod_meta_file].decompress())

def get_mod_name(rs5, filename):
	try:
		meta = get_mod_meta(rs5)
	except:
		# Fall through
		pass
	else:
		if 'NAME' in meta:
			return meta['NAME'].data.strip()
	return os.path.splitext(os.path.basename(filename))[0]

def add_mod(dest_archive, source_archives):
	rs5 = Rs5ModArchiveUpdater(open(dest_archive, 'rb+'))
	do_add_undo(rs5)
	for source_archive in source_archives:
		source_rs5 = rs5archive.Rs5ArchiveDecoder(open(source_archive, 'rb'))
		mod_name = get_mod_name(source_rs5, source_archive)

		manifest_name = '%s\\%s.manifest' % (mod_manifests, mod_name)
		modinfo_name = '%s\\%s.modinfo' % (mod_manifests, mod_name)
		if manifest_name in rs5:
			do_rm_mod(rs5, mod_name)

		mod_entries = ModCentralDirectoryEncoder(mod_name, rs5.ent_len)
		for source_file in source_rs5.itervalues():
			if file_blacklisted(source_file.filename):
				print 'Skipping %s' % source_file.filename
				continue
			print 'Adding %s->%s...' % (source_archive, source_file.filename)
			entry = rs5archive.Rs5CompressedFileRepacker(rs5.fp, source_file, seek_cb=rs5.seek_find_hole)
			if entry.filename == mod_meta_file:
				entry.filename = modinfo_name
			rs5[entry.filename] = entry
			mod_entries[entry.filename] = entry
		rs5.add_from_buf(mod_entries.encode())
	apply_mod_order(rs5)
	rs5.save()
	rs5.truncate_eof()

# vi:noexpandtab:sw=8:ts=8
