#!/usr/bin/env python2
import sys
from os.path import dirname, realpath

sys.path.append(realpath(dirname(__file__)))
from gimpfu import main, pdb
from _plugin_base import GimpPluginBase


class WaifuXL(GimpPluginBase):
    def run(self):
        self.model_file = 'WaifuXL.py'
        result = self.predict(self.drawable)
        h, w, d = result.shape
        self.gimp_img.resize(w, h, 0, 0)
        self.create_layer(result)


plugin = WaifuXL()
plugin.register(
    proc_name="waifuxl",
    blurb="waifuxl",
    help="2x Upscale using WaifuXL (https://github.com/TheFutureGadgetsLab/WaifuXL)",
    author="yantoz",
    copyright="",
    date="2023",
    label="Super Resolution (WaifuXL) ...",
    imagetypes="RGB*"
)
main()
