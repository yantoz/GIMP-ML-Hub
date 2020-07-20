#!/usr/bin/env python2
import sys
from os.path import dirname, realpath

sys.path.append(realpath(dirname(__file__)))
from gimpfu import main, pdb
from _plugin_base import GimpPluginBase


class SuperResolution(GimpPluginBase):
    def run(self):
        self.model_file = 'SRResNet.py'
        result = self.predict(self.drawable)
        h, w, d = result.shape
        self.gimp_img.resize(w, h, 0, 0)
        self.create_layer(result)


plugin = SuperResolution()
plugin.register(
    proc_name="super-resolution",
    blurb="super-resolution",
    help="Running super-resolution.",
    author="Kritik Soman",
    copyright="",
    date="2020",
    label="super-resolution...",
    imagetypes="RGB*"
)
main()
