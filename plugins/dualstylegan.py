#!/usr/bin/env python2
import sys
from os.path import dirname, realpath

sys.path.append(realpath(dirname(__file__)))
import gimpfu as gfu
from _plugin_base import GimpPluginBase


class DualStyleGAN(GimpPluginBase):

    def run(self, style_num, style_id, style_degree, color_transfer, keep_size):
        self.model_file = "DualStyleGAN.py"
        self.name = _style_list[style_num][0]
        gfu.gimp.progress_init("Running DualStyleGAN ({}) ...".format(self.name))
        layer = self.drawable
        result = self.predict(layer, _style_list[style_num][1], style_id, style_degree, color_transfer, keep_size)
        if not result:
            return
        #h, w, _ = result.shape
        #self.gimp_img.resize(w, h, 0, 0)
        newlayer = self.create_layer(
            result, name=self.drawable.name + ":" + _style_list[style_num][0]
        )
	newlayer.set_offsets(layer.offsets[0], layer.offsets[1])


_style_list = [
    ("arcane",      "arcane"),
    ("anime",       "anime"),
    ("caricature",  "caricature"),
    ("cartoon",     "cartoon"),
    ("comic",       "comic"),
    ("pixar",       "pixar"),
    ("slamdunk",    "slamdunk"),
]

_style_params = (name for i, (name, style) in enumerate(_style_list))

plugin = DualStyleGAN()
plugin.register(
    proc_name="dualstylegan",
    blurb="DualStyleGAN\nSee: https://github.com/williamyang1991/DualStyleGAN/tree/main/doc_images",
    help="Exemplar-Based High-Resolution Portrait Style Transfer",
    author="yantoz",
    copyright="",
    date="2023",
    label="Style Transfer (DualStyleGAN) ...",
    imagetypes="RGB*",
    params=[
        (gfu.PF_OPTION, "style", "Style:", 0, _style_params),
        (gfu.PF_INT,    "style_id", "Style ID", 26),
        (gfu.PF_FLOAT,  "style_degree", "Style Degree", 0.5),
        (gfu.PF_BOOL,   "color_transfer", "Color Transfer", False),
        (gfu.PF_BOOL,   "keep_size", "Keep Size", True),
    ],
)
gfu.main()
