#!/usr/bin/env python

import sys, os
import threading

# # --- PyQt4 ---
# from PyQt4 import QtCore, QtGui, uic
# QtCore.Slot = QtCore.pyqtSlot

# --- PySide ---
import PySide
from PySide import QtCore, QtGui
sys.modules['PyQt4'] = PySide # ImageQt is hardcoded to use PyQt4

import Image, ImageDraw, ImageQt
from savemanager_ui import Ui_SaveManager

def find_miasmata_install():
	import _winreg
	key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
			'SOFTWARE\\IonFX\\Miasmata', 0,
			_winreg.KEY_READ | _winreg.KEY_WOW64_32KEY)
	return _winreg.QueryValueEx(key, 'Install_Path')[0]

def find_miasmata_save():
	import winpaths
	return os.path.join(winpaths.get_appdata(),
			'IonFx', 'Miasmata', 'saves.dat')
	# return os.path.join(os.path.expanduser('~'), 'AppData', 'Roaming',
	# 		'IonFx', 'Miasmata', 'saves.dat')

class MiasmataSaveUtil(QtGui.QWidget):
	def __init__(self, parent=None):
		super(MiasmataSaveUtil, self).__init__(parent)

		self.ui = Ui_SaveManager()
		self.ui.setupUi(self) # doesn't work with a dynamically loaded UI

		try:
			install_path = find_miasmata_install()
			self.ui.install_path.setText(install_path)
			self.process_install_path(install_path)
		except:
			pass

		try:
			save_path = find_miasmata_save()
			self.ui.save_path.setText(save_path)
			self.process_save_path(save_path)
		except:
			pass

	def __del__(self):
		del self.ui

	def progress(self, msg):
		if not hasattr(self, 'busy') or not self.busy:
			QtGui.QApplication.setOverrideCursor(QtCore.Qt.WaitCursor)
		self.busy = True
		self.ui.progress.setText(msg)
		self.ui.progress.repaint()
		self.repaint()

	def done(self, msg='Done'):
		QtGui.QApplication.restoreOverrideCursor()
		self.busy = False
		self.ui.progress.setText(msg)

	def process_install_path(self, path):
		import rs5archive, rs5file, imag
		# def _async():
		main_path = os.path.join(path, 'main.rs5')
		self.progress('Loading main.rs5...')
		try:
			self.rs5main = rs5archive.Rs5ArchiveDecoder(open(main_path, 'rb'))
			self.progress('main.rs5 Loaded')
		except Exception, e:
			self.done('%s loading main.rs5: %s' % (e.__class__.__name__, str(e)))
			return

		self.progress('Extracting Map_FilledIn...')
		filledin = rs5file.Rs5ChunkedFileDecoder(self.rs5main['TEX\\Map_FilledIn'].decompress())
		self.progress('Decoding Map_FilledIn...')
		self.filledin = imag.open_rs5file_imag(filledin, (1024, 1024), 'RGB')

		self.progress('Extracting Map_OverlayInfo...')
		overlayinfo = rs5file.Rs5ChunkedFileDecoder(self.rs5main['TEX\\Map_OverlayInfo'].decompress())
		self.progress('Decoding Map_OverlayInfo...')
		self.overlayinfo = imag.open_rs5file_imag(overlayinfo, (1024, 1024), 'RGB')

		self.done()

		# Python's GIL still causes UI thread to starve. Can I use
		# multiprocessing for this?
		# t = threading.Thread(target=_async)
		# t.daemon = True
		# t.run()

	def enable_save_slots(self, slots):
		self.ui.save0.setEnabled('save0' in slots)
		self.ui.save1.setEnabled('save1' in slots)
		self.ui.save2.setEnabled('save2' in slots)

	def process_save_path(self, path):
		import data
		self.progress('Loading saves...')
		try:
			self.saves = data.parse_data(open(path, 'rb'))
			self.done('Saves Loaded')
		except Exception, e:
			self.done('%s loading main.rs5: %s' % (e.__class__.__name__, str(e)))
			return
		enable_slots = filter(lambda x: self.saves[x]['text_description'] != None,
				['save0', 'save1', 'save2'])
		# self.enable_save_slots(self.saves.children.keys())
		self.enable_save_slots(enable_slots)

	def show_image(self, image):
		self.progress('Rendering...')
		image1 = ImageQt.ImageQt(image)
		# Using an ImageQt crashes python on Windows, make a
		# (non-shallow) copy of the image to turn it into a real
		# QImage so it won't crash:
		image2 = image1.copy()
		pixmap = QtGui.QPixmap.fromImage(image2)
		label = QtGui.QLabel('', self.ui.scrollArea)
		label.setPixmap(pixmap)
		self.ui.scrollArea.setWidget(label)
		self.done()

	def main_rs5_loaded(self):
		return hasattr(self, 'filledin') and hasattr(self, 'overlayinfo')

	def coord(self, (x, y)):
		# Game coords are rotated 90 degrees clockwise and in the range
		# 8192.0 x 8192.0. Rotate coord 90 degrees counter-clockwise
		# (transpose then mirror y), then divide by 8.
		return map(int, (y / 8, (8192 - x) / 8))

	def gen_map(self, save):
		import exposure_map
		if not self.main_rs5_loaded():
			self.process_install_path(self.ui.install_path.text())
		if not self.main_rs5_loaded():
			self.done('Fill in your Miasmata install location!')
			return

		self.progress('Extracting exposure_map...')
		exp = str(save['player']['MAP']['exposure_map'])
		self.progress('Generating map...')
		(self.map, self.outline_mask, self.filledin_mask) = \
				exposure_map.gen_map(exp, self.filledin, self.overlayinfo)

		self.show_image(self.map)

	def show_coast(self):
		import exposure_map

		self.progress('Darkening...')
		image = Image.eval(self.map, lambda x: x/4)
		exposure_map.overlay_smap(image, self.shoreline, self.outline_mask, self.filledin_mask)
		self.show_image(image)
	@QtCore.Slot()
	def on_show_coast_clicked(self):
		self.show_coast()

	def coast_progress(self, save):
		import rs5file, smap

		self.progress('Extracting player_map_achievements...') # XXX: Also in environment.rs5
		self.shoreline = rs5file.Rs5ChunkedFileDecoder(self.rs5main['player_map_achievements'].decompress())

		revealed = 0
		filledin_pix = self.filledin_mask.load()

		for (total, (x, y)) in enumerate(smap.smap_iter(self.shoreline, self.map.size[0]), 1):
			if filledin_pix[x, y]:
				revealed += 1

		self.ui.coast.setText('%i%% (%i/%i)' % (revealed * 100 / total, revealed, total))
		self.ui.lbl_coast.setEnabled(True)
		self.ui.show_coast.setEnabled(True)

		self.done()

	def urn_iter(self, save):
		# XXX TODO: Read urns from markers file and match these up -
		# Seems that sometimes camp fires do get counted?
		urns = save['state']['urns']
		for urn in urns.itervalues():
			pos = list(urn['pos'])
			yield (urn['touched'], self.coord(pos[:2]))

	def count_touched_urns(self, save):
		urns_lit = filter(lambda (t, pos): t, self.urn_iter(save))
		self.ui.urns.setText(str(len(urns_lit)))
		self.ui.lbl_urns.setEnabled(True)
		self.ui.show_urns.setEnabled(True)

	def show_urn_progress(self):
		if not hasattr(self, 'map'):
			self.gen_map(self.save)

		self.progress('Darkening...')
		image = Image.eval(self.map, lambda x: x/2)
		draw = ImageDraw.Draw(image)

		self.progress('Plotting Urns...')
		for (t, (x, y)) in self.urn_iter(self.save):
			c = (255, 0, 0)
			if t:
				c = (0, 255, 0)
			draw.rectangle((x-5, y-5, x+5, y+5), outline=c)
		self.show_image(image)
	@QtCore.Slot()
	def on_show_urns_clicked(self):
		self.show_urn_progress()

	def count_notes(self, save):
		notes = save['player']['journal']['notes']
		if notes == None:
			notes = {}
		removed = save['inst_tree']['removed_types']
		self.ui.notes.setText(str(len(notes)))
		self.ui.lbl_notes.setEnabled(True)
		if 'modelsets\\NoteZZ' in removed and 'NoteZZ' not in notes:
			self.ui.reset_notezz.setEnabled(True)

	def count_plants(self, save):
		plants = save['player']['journal']['plants'].keys()
		if plants == None:
			plants = []
		plants = filter(lambda x: x.lower().startswith('plant'), plants)
		self.ui.plants.setText(str(len(plants)))
		self.ui.lbl_plants.setEnabled(True)

	@QtCore.Slot()
	def on_reset_notezz_clicked(self):
		import data, time
		save_path = self.ui.save_path.text()
		self.progress('Writing %s...' % save_path)

		try:
			timestamp_str = time.strftime('%Y%m%d%H%M%S')
			backup = '%s~%s' % (save_path, timestamp_str)
			os.rename(save_path, backup)
		except Exception, e:
			self.done('%s backing up saves.dat: %s' % (e.__class__.__name__, str(e)))
			return

		self.save['inst_tree']['removed_types'].remove('modelsets\\NoteZZ')

		open(save_path, 'wb').write(data.encode(self.saves))

		self.ui.reset_notezz.setEnabled(False)
		self.process_save_path(save_path)
		self.done('Backup written to %s' % backup)

	def clear_progress(self):
		self.ui.lbl_coast.setEnabled(False)
		self.ui.show_coast.setEnabled(False)
		self.ui.coast.setText('')
		self.ui.lbl_urns.setEnabled(False)
		self.ui.show_urns.setEnabled(False)
		self.ui.urns.setText('')
		self.ui.lbl_heads.setEnabled(False)
		self.ui.show_heads.setEnabled(False)
		self.ui.reset_head.setEnabled(False)
		#self.ui.heads.setText('')
		self.ui.lbl_notes.setEnabled(False)
		self.ui.reset_notezz.setEnabled(False)
		self.ui.notes.setText('')
		self.ui.lbl_plants.setEnabled(False)
		self.ui.plants.setText('')

	def process_save(self, save):
		# Ensure we are up to date:
		self.clear_progress()
		save_path = self.ui.save_path.text()
		self.process_save_path(save_path)

		try:
			self.save = self.saves[save]
			self.count_touched_urns(self.save)
			self.count_notes(self.save)
			self.count_plants(self.save)
			self.gen_map(self.save)
			self.coast_progress(self.save)
		except Exception, e:
			self.done('%s processing %s: %s' % (e.__class__.__name__, save, str(e)))

	@QtCore.Slot()
	def on_save0_clicked(self): self.process_save('save0')
	@QtCore.Slot()
	def on_save1_clicked(self): self.process_save('save1')
	@QtCore.Slot()
	def on_save2_clicked(self): self.process_save('save2')

	@QtCore.Slot()
	def on_install_browse_clicked(self):
		install_path = self.ui.install_path.text()
		dialog = QtGui.QFileDialog(self,
				caption="Select Miasmata Install Location...",
				directory=install_path)
		dialog.setFileMode(QtGui.QFileDialog.Directory)
		if not dialog.exec_():
			return
		install_path = dialog.selectedFiles()
		self.process_install_path(install_path)
		self.ui.install_path.setText(install_path[0])

	@QtCore.Slot()
	def on_install_path_returnPressed(self):
		install_path = self.ui.install_path.text()
		self.process_install_path(install_path)

	@QtCore.Slot()
	def on_save_browse_clicked(self):
		save_path = self.ui.save_path.text()
		save_path = QtGui.QFileDialog.getOpenFileName(self,
				"Select Miasmata Saved Game...",
				save_path)
		if not save_path:
			return
		self.ui.save_path.setText(save_path)
		self.process_save_path(save_path)

	@QtCore.Slot()
	def on_save_path_returnPressed(self):
		save_path = self.ui.save_path.text()
		self.process_save_path(save_path)

if __name__ == '__main__':
	import multiprocessing
	multiprocessing.freeze_support()

	app = QtGui.QApplication(sys.argv)
	dialog = MiasmataSaveUtil()

	dialog.show()
	app.exec_()
	# If using PyQt4, this prevents "python.exe has stopped working..." on
	# close (Seems unnecessary with PySide):
	del dialog
