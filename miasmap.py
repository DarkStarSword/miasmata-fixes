#!/usr/bin/env python

from PIL import Image
import sys, os

width = 8238
height = 8193
minz = -1815
maxz = 1833

width = 4096
height = 4096
scale = 2

map_filledin_path = 'Map_FilledIn.jpg'
if not os.path.isfile(map_filledin_path):
	# TODO: Extract from main.rs5
	map_filledin_path = os.path.join(os.path.dirname(__file__), map_filledin_path)
try:
	image = Image.open(map_filledin_path).transpose(Image.ROTATE_270).resize((width, height))
except:
	import traceback
	traceback.print_exc()
	image = Image.new('RGB', (width, height), (0,0,0))
image = Image.eval(image, lambda x: x/3)
pix = image.load()

def save_image(filename):
	print>>sys.stderr, 'Saving %s...' % filename
	image.transpose(Image.ROTATE_90).save(filename)

def plot(x, y, (r, g, b), additive=True):
	x = max(0, min(x / scale, width-1))
	y = max(0, min(y / scale, height-1))

	if additive:
		(r1, g1, b1) = pix[x, y]
		pix[x, y] = (r1 + r, g1 + g, b1 + b)
	else:
		pix[x, y] = (r, g, b)

def plot_rect(x1, y1, c1, x2, y2, c2):
	xr = x2 - x1
	yr = y2 - y1
	def interpolate(p):
		return [ int(p*v1 + (1.0-p)*v2) for (v1,v2) in zip(c1, c2) ]
	for x in range(x1, x2+1, scale):
		p = float(x - x1) / xr
		p1 = p / 2.0
		p2 = p1 + 0.5
		rgb1 = interpolate(p1)
		rgb2 = interpolate(p2)
		plot(x, y1, rgb1)
		plot(x, y2, rgb2)
	for y in range(y1+1, y2, scale):
		p = float(y - y1) / yr
		p1 = p / 2.0
		p2 = p1 + 0.5
		rgb1 = interpolate(p1)
		rgb2 = interpolate(p2)
		plot(x1, y, rgb1)
		plot(x2, y, rgb2)

def plot_point(x, y, rgb1 = (255, 255, 255), rgb2 = (192, 192, 192)):
	plot(x, y, rgb1)
	for (xx, yy) in ((x-1*scale, y), (x+1*scale, y), (x, y-1*scale), (x, y+1*scale)):
		plot(xx, yy, rgb2)

def plot_cross(x, y, d = 20, rgb = (255, 255, 255)):
	for (x1, y1) in zip(range(x-d, x+d), range(y-d, y+d)):
		plot(x1, y1, rgb)
	for (x1, y1) in zip(reversed(range(x-d, x+d)), range(y-d, y+d)):
		plot(x1, y1, rgb)

def plot_square(x, y, d = 20, rgb = (255, 255, 255), additive=True):
	for y1 in range(y-d, y+d, scale):
		for x1 in range(x-d, x+d, scale):
			plot(x1, y1, rgb, additive)

# vi:noexpandtab:sw=8:ts=8
