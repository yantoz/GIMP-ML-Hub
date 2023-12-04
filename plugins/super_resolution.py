#!/usr/bin/env python2
import sys
from os.path import dirname, realpath

sys.path.append(realpath(dirname(__file__)))
import gimpfu as gfu
from _plugin_base import GimpPluginBase


class SuperResolution(GimpPluginBase):
    def run(self, force_cpu):
        self.model_file = 'SRResNet.py'
        result = self.predict(self.drawable, force_cpu=force_cpu)
        if not result:
            return
        h, w, d = result.shape
        self.gimp_img.resize(w, h, 0, 0)
        self.create_layer(result)


plugin = SuperResolution()
plugin.register(
    proc_name="super-resolution",
    blurb="SRResNet\nSuper Resolution",
    help="https://github.com/twtygqyy/pytorch-SRResNet",
    author="Kritik Soman",
    copyright="",
    date="2020",
    label="Super Resolution (SRResNet) ...",
    imagetypes="RGB*",
    params = [
        (gfu.PF_BOOL, "force_cpu", "Force CPU", False),
    ],
)
