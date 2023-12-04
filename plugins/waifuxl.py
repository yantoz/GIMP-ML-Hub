#!/usr/bin/env python2
import sys
from os.path import dirname, realpath

sys.path.append(realpath(dirname(__file__)))
import gimpfu as gfu
from _plugin_base import GimpPluginBase


class WaifuXL(GimpPluginBase):
    def run(self, force_cpu):
        self.model_file = 'WaifuXL.py'
        result = self.predict(self.drawable, force_cpu=force_cpu)
        if not result:
            return
        h, w, d = result.shape
        self.gimp_img.resize(w, h, 0, 0)
        self.create_layer(result)


plugin = WaifuXL()
plugin.register(
    proc_name="waifuxl",
    blurb="WaifuXL\n2x Upscale",
    help="https://github.com/TheFutureGadgetsLab/WaifuXL",
    author="yantoz",
    copyright="",
    date="2023",
    label="Super Resolution (WaifuXL) ...",
    imagetypes="RGB*",
    params = [
        (gfu.PF_BOOL, "force_cpu", "Force CPU", False),
    ],
)
