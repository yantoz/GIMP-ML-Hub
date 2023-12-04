#!/usr/bin/env python2
import sys
from os.path import dirname, realpath

sys.path.append(realpath(dirname(__file__)))
import gimpfu as gfu
from _plugin_base import GimpPluginBase


class FaceParse(GimpPluginBase):
    def run(self, force_cpu):
        self.model_file = 'FaceParse_BiSeNet.py'
        result = self.predict(self.drawable, force_cpu=force_cpu)
        if result:
            self.create_layer(result)


plugin = FaceParse()
plugin.register(
    proc_name="faceparse",
    blurb="Face Parsing",
    help="https://github.com/zllrunning/face-parsing.PyTorch",
    author="Kritik Soman",
    copyright="",
    date="2020",
    label="Face Parse (BiSeNet) ...",
    imagetypes="RGB*",
    params = [
        (gfu.PF_BOOL, "force_cpu", "Force CPU", False),
    ],
)
