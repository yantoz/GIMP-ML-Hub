#!/usr/bin/env python2
import sys
from os.path import dirname, realpath

sys.path.append(realpath(dirname(__file__)))
from gimpfu import main
from _plugin_base import GimpPluginBase


class Deblur(GimpPluginBase):
    def run(self):
        self.model_file = 'DeblurGANv2.py'
        result = self.predict(self.drawable)
        self.create_layer(result)


plugin = Deblur()
plugin.register(
    proc_name="deblur",
    blurb="deblur",
    help="Running deblurring.",
    author="Kritik Soman",
    copyright="",
    date="2020",
    label="Deblur (DeblurGANv2) ...",
    imagetypes="RGB*"
)
main()
