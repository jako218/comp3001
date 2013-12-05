#!/usr/bin/python
"""
Hexagon Image Processing Class
"""
from PIL import Image, ImageOps, ImageDraw
from StringIO import StringIO
import urllib2

class Hexagon:

	def __init__(self, url):
		self.hex = self.create_hex(url)

	def create_hex(self, url):
		size = (1000, 864)
		mask = Image.new('L', size, 0)
		draw = ImageDraw.Draw(mask) 
		draw.polygon([(0, 432), (250, 0), (750, 0), (1000, 432), (750, 864), (250, 864)], fill=255)
		im = Image.open(StringIO(urllib2.urlopen(url).read()))
		hexagon = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
		hexagon.putalpha(mask)
		hexagon.thumbnail((500,500), Image.ANTIALIAS)
		output = StringIO()
		hexagon.save(output, format="png")
		return output.getvalue()

	def get_hex(self):
		return self.hex