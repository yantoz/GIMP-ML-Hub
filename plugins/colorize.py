#!/usr/bin/env python2
import sys
from os.path import dirname, realpath

sys.path.append(realpath(dirname(__file__)))
from gimpfu import pdb
import gimpfu as gfu
from _plugin_base import GimpPluginBase


class Colorize(GimpPluginBase):
    def run(self, force_cpu):
        self.model_file = 'NeuralColorization.py'
        result = self.predict(self.drawable, force_cpu=force_cpu)
        if self.gimp_img.base_type != gfu.RGB:
            pdb.gimp_image_convert_rgb(self.gimp_img)
        if result:
            self.create_layer(result)


plugin = Colorize()
plugin.register(
    proc_name="colorize",
    blurb="Neural-Colorization\nGAN for Image Colorization",
    help="https://github.com/zeruniverse/neural-colorization",
    author="Kritik Soman",
    copyright="",
    date="2020",
    label="Colorize (NeuralColorization) ...",
    imagetypes="RGB*, GRAY*",
    params=[
        (gfu.PF_BOOL, "force_cpu", "Force CPU", False),
    ],
)
