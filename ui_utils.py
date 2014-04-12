#!/usr/bin/env python

from PySide import QtGui
import sys

def catch_error(f):
	import functools
	@functools.wraps(f)
	def catch_unhandled_exceptions(*args, **kwargs):
		try:
			return f(*args, **kwargs)
		except Exception as e:
			import traceback
			traceback.print_exc()
			sys.stderr.flush()
			dialog = QtGui.QMessageBox()
			dialog.setWindowTitle('MiasMod')
			dialog.setIcon(QtGui.QMessageBox.Critical)
			dialog.setText(QtGui.QApplication.translate('Errors', 'Unhandled Exception', None, QtGui.QApplication.UnicodeUTF8))
			dialog.setInformativeText('%s: %s' % (e.__class__.__name__, str(e)))
			dialog.setDetailedText(traceback.format_exc())
			dialog.exec_()
			return
	return catch_unhandled_exceptions

# vi:noexpandtab:sw=8:ts=8
