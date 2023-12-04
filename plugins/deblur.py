#!/usr/bin/env python2
import sys
from os.path import dirname, realpath

sys.path.append(realpath(dirname(__file__)))
import gimpfu as gfu
from _plugin_base import GimpPluginBase


class Deblur(GimpPluginBase):
    def run(self, force_cpu):
        self.model_file = 'DeblurGANv2.py'
        result = self.predict(self.drawable, force_cpu=force_cpu)
        if result:
            self.create_layer(result)


plugin = Deblur()
plugin.register(
    proc_name="deblur",
    blurb="DeblurGANv2\nDeblurring Faster and Better",
    help="https://github.com/VITA-Group/DeblurGANv2",
    author="Kritik Soman",
    copyright="",
    date="2020",
    label="Deblur (DeblurGANv2) ...",
    imagetypes="RGB*",
    params = [
        (gfu.PF_BOOL, "force_cpu", "Force CPU", False),
    ]
)
