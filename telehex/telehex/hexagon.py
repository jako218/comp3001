#!/usr/bin/env python
"""
:mod:`hexagon` -- Converts images to hexagons
===============================================

.. module:: hexagon
   :synopsis: Deals with creating hexagons from an image specified in a url

.. moduleauthor:: Miles Armstrong <mhha1g11@ecs.soton.ac.uk>
.. moduleauthor:: Simon Bidwell <sab3g11@ecs.soton.ac.uk>
.. moduleauthor:: Will Buss <wjb1g11@ecs.soton.ac.uk>
.. moduleauthor:: Jamie Davies <jagd1g11@ecs.soton.ac.uk>
.. moduleauthor:: Hayden Eskriett <hpe1g11@ecs.soton.ac.uk>
.. moduleauthor:: Jack Flann <jof1g11@ecs.soton.ac.uk>
.. moduleauthor:: Chantel Spencer-Bowdage <csb1g11@ecs.soton.ac.uk>
"""

from PIL import Image, ImageOps, ImageDraw
from StringIO import StringIO
import urllib2


class Hexagon:
    """
    A Class used to create hexagon pngs from a given url
    """

    def __init__(self, url):
        """
        Takes an image an converts it into a hexagon

        :param url: The image url to be converted to a hexagon png
        """

        # Specify the size of the image to draw
        size = (1000, 864)

        # Create a new mask, with mode set to 'L' for luminance and a color of 0
        mask = Image.new('L', size, 0)

        # Create a new ImageDraw instance
        draw = ImageDraw.Draw(mask)

        # Draw a hexagon on the mask
        draw.polygon([(0, 432), (250, 0), (750, 0), (1000, 432), (750, 864), (250, 864)], fill=255)

        try:
            # Open the image specified by the url
            im = Image.open(StringIO(urllib2.urlopen(url).read()))
            # Put the mask in the center of the image from the url
            hexagon = ImageOps.fit(im, mask.size, centering=(0.5, 0.5))
            hexagon.putalpha(mask)

            # Resize the image to 500 x 500 px
            hexagon.thumbnail((500, 500), Image.ANTIALIAS)

            # Output the contents of the image as a string which allows the hexa to be saved as a blob in the datastore
            output = StringIO()
            hexagon.save(output, format="png")
            self.hex = output.getvalue()

        except urllib2.HTTPError:
            self.hex = None

    def get_hex(self):
        """
        Gets the hexagon image

        :return: A string representation of the image
        """
        return self.hex
