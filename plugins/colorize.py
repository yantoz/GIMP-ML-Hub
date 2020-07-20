#!/usr/bin/env python2
import sys
from os.path import dirname, realpath

sys.path.append(realpath(dirname(__file__)))
from gimpfu import main, pdb
import gimpfu as gfu
from _plugin_base import GimpPluginBase


class Colorize(GimpPluginBase):
    def run(self):
        self.model_file = 'NeuralColorization.py'
        result = self.predict(self.drawable)
        if self.gimp_img.base_type != gfu.RGB:
            pdb.gimp_image_convert_rgb(self.gimp_img)
        self.create_layer(result)


plugin = Colorize()
plugin.register(
    proc_name="colorize",
    blurb="colorize",
    help="Colorize grayscale images",
    author="Kritik Soman",
    copyright="",
    date="2020",
    label="colorize...",
    imagetypes="RGB*, GRAY*"
)
main()
