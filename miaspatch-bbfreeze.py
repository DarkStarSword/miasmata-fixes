#!/usr/bin/env python

import shutil, sys, os
extractor = __import__('rs5-extractor')
import ConfigParser

binary_patches = ['botanical']
delete = ['communitypatch.rs5']
copy_language_src = True

# TODO: Have langauge settings & extra miasmod/rs5mod files passed in on the command line
order = ['communitypatch', 'french']
language = 'fr_FR'
extra_files = [
	os.path.join('translations', 'french.miasmod'),
	os.path.join('translations', 'french.rs5mod')
]

for file in extra_files:
	if not os.path.isfile(file):
		print '%s does not exist, exiting!' % file
		sys.exit(1)

from bbfreeze import Freezer
f = Freezer("miaspatch")
f.include_py = False
f.addScript("miaspatch.py", gui_only=True)
for patch in binary_patches:
	f.addModule(patch)
f()

src = os.path.join('communitypatch', 'communitypatch.miasmod')
dst = os.path.join('miaspatch', 'communitypatch.miasmod')
shutil.copyfile(src, dst)

src = os.path.join('communitypatch', 'main')
dst = os.path.join('miaspatch', 'communitypatch.rs5mod')
extractor.create_rs5(dst, [src], True)

for file in extra_files:
	dst = os.path.join('miaspatch', os.path.basename(file))
	shutil.copyfile(file, dst)

if language is not None:
	dst_dir = os.path.join('miaspatch', 'miaspatch_i18n')
	if not os.path.isdir(dst_dir):
		os.mkdir(dst_dir)
	if copy_language_src:
		src = os.path.join('miaspatch_i18n', '%s.ts' % language)
		dst = os.path.join(dst_dir, '%s.ts' % language)
		if os.path.isfile(src):
			shutil.copyfile(src, dst)
	src = os.path.join('miaspatch_i18n', '%s.qm' % language)
	dst = os.path.join(dst_dir, '%s.qm' % language)
	if os.path.isfile(src):
		shutil.copyfile(src, dst)

dst = os.path.join('miaspatch', 'miaspatch.cfg')
config = ConfigParser.RawConfigParser()
if binary_patches:
	config.set('DEFAULT', 'binary_patches', ' '.join(binary_patches))
if delete:
	config.set('DEFAULT', 'delete', ' '.join(delete))
if language is not None:
	config.set('DEFAULT', 'language', language)
if order:
	config.set('DEFAULT', 'prefix_order', ' '.join(order))
with open(dst, 'wb') as configfile:
    config.write(configfile)

# vi:noexpandtab:sw=8:ts=8
