#!/usr/bin/env python2
import sys
from os.path import dirname, realpath

sys.path.append(realpath(dirname(__file__)))
import gimpfu as gfu
from _plugin_base import GimpPluginBase


class DepthEstimation(GimpPluginBase):
    model_options = [
        ("MiDaS (778 MB)", "MiDaS.py"),
        ("Monodepth2 (112 MB)", "Monodepth2.py"),
    ]

    def run(self, model_idx, apply_colormap, force_cpu):
        display_name, self.model_file = self.model_options[model_idx]
        colormap = "magma" if apply_colormap else None
        result = self.predict(self.drawable, colormap, force_cpu=force_cpu)
        if not result:
            return
        layer_name = self.drawable.name + " " + display_name.split()[0]
        self.create_layer(result, name=layer_name)


plugin = DepthEstimation()
plugin.register(
    proc_name="depth_estimation",
    blurb="Monodepth2\nGenerate an inverse depth map based on deep learning",
    help="https://github.com/nianticlabs/monodepth2",
    author="Martin Valgur",
    copyright="",
    date="2020",
    label="Depth Estimation (MiDaS/Monodepth2) ...",
    imagetypes="RGB*",
    params=[
        (gfu.PF_OPTION, "Model",     "Model",          0,       [x[0] for x in DepthEstimation.model_options]),
        (gfu.PF_TOGGLE, "Colormap",  "Apply colormap", 0,       True),
        (gfu.PF_BOOL,   "force_cpu", "Force CPU",      False),
    ]
)
