#!/usr/bin/env python

import os

def find_miasmata_install():
	import _winreg
	key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
			'SOFTWARE\\IonFX\\Miasmata', 0,
			_winreg.KEY_READ | _winreg.KEY_WOW64_32KEY)
	ret = _winreg.QueryValueEx(key, 'Install_Path')[0]
	if not os.path.isdir(ret):
		raise IOError('Miasmata install path from registry does not exist')
	return ret

def find_miasmata_save():
	import winpaths, os
	return os.path.join(winpaths.get_appdata(),
			'IonFx', 'Miasmata', 'saves.dat')
	# return os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming',
	# 		'IonFx', 'Miasmata', 'saves.dat')

# vi:noexpandtab:sw=8:ts=8
