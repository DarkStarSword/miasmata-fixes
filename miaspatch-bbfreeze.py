#!/usr/bin/env python

import shutil, sys, os
extractor = __import__('rs5-extractor')
import ConfigParser
import argparse

binary_patches = ['botanical']
delete = ['communitypatch.rs5']
copy_language_src = False
order = ['communitypatch']

parser = argparse.ArgumentParser()
parser.add_argument('-l', '--language', help='Language pack to include and enable')
parser.add_argument('-x', '--exe-translation', help='Translations for hard coded strings to binary patch')
parser.add_argument('-d', '--dest', '--dist', default='miaspatch', help='Destination directory')
parser.add_argument('mods', nargs='*', help='Extra mods (asside from the community patch) to include')
args = parser.parse_args()

if args.language is not None:
	if not os.path.isfile(os.path.join('miaspatch_i18n', '%s.ts' % args.language)):
		if not os.path.isfile(os.path.join('miaspatch_i18n', '%s.qm' % args.language)):
			print '%s language pack does not exist, exiting!' % args.language
			sys.exit(1)

if args.exe_translation is not None:
	binary_patches.append('translate_exe')
	args.mods.append(args.exe_translation)

for file in args.mods:
	if not os.path.isfile(file):
		print '%s does not exist, exiting!' % file
		sys.exit(1)
	(name, ext) = os.path.splitext(os.path.basename(file))
	if ext.lower() == '.rs5mod':
		order.append(name)
print 'Mod order:', order

from bbfreeze import Freezer
f = Freezer(args.dest)
f.include_py = False
f.addScript("miaspatch.py", gui_only=True)
for patch in binary_patches:
	f.addModule(patch)
f()

src = os.path.join('communitypatch', 'communitypatch.miasmod')
dst = os.path.join(args.dest, 'communitypatch.miasmod')
shutil.copyfile(src, dst)

src = os.path.join('communitypatch', 'main')
dst = os.path.join(args.dest, 'communitypatch.rs5mod')
extractor.create_rs5(dst, [src], True)

for file in args.mods:
	dst = os.path.join(args.dest, os.path.basename(file))
	shutil.copyfile(file, dst)

if args.language is not None:
	dst_dir = os.path.join(args.dest, 'miaspatch_i18n')
	if not os.path.isdir(dst_dir):
		os.mkdir(dst_dir)
	if copy_language_src:
		src = os.path.join('miaspatch_i18n', '%s.ts' % args.language)
		dst = os.path.join(dst_dir, '%s.ts' % args.language)
		if os.path.isfile(src):
			shutil.copyfile(src, dst)
	src = os.path.join('miaspatch_i18n', '%s.qm' % args.language)
	dst = os.path.join(dst_dir, '%s.qm' % args.language)
	if os.path.isfile(src):
		shutil.copyfile(src, dst)

dst = os.path.join(args.dest, 'miaspatch.cfg')
config = ConfigParser.RawConfigParser()
if binary_patches:
	config.set('DEFAULT', 'binary_patches', ' '.join(binary_patches))
if delete:
	config.set('DEFAULT', 'delete', ' '.join(delete))
if args.language is not None:
	config.set('DEFAULT', 'language', args.language)
if args.exe_translation:
	config.set('DEFAULT', 'exe_translation', os.path.basename(args.exe_translation))
if order:
	config.set('DEFAULT', 'prefix_order', ' '.join(order))
with open(dst, 'wb') as configfile:
    config.write(configfile)

# vi:noexpandtab:sw=8:ts=8
