#!/usr/bin/env python

from distutils.core import setup
import py2exe

# Change console to windows to suppress terminal window

# --- PySide ---
setup(windows=['savemanager.pyw'],
	options = {
		"py2exe": {
			"dll_excludes": ["MSVCP90.dll"]
		}
	}
)

# # --- PyQt4 ---
# # If py2exe craps out with an invalid syntax error in PyQt4, just delete the
# # port_v3 directory.
# setup(windows=['savemanager.pyw'],
# 	options = {
# 		"py2exe": {
# 			"includes": ["sip"],
# 			"dll_excludes": ["MSVCP90.dll"]
# 		}
# 	}
# )
