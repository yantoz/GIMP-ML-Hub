#!/usr/bin/env python2
import sys
from os.path import dirname, realpath

sys.path.append(realpath(dirname(__file__)))
import gimpfu as gfu
from _plugin_base import GimpPluginBase


class ESRGAN(GimpPluginBase):
    def run(self, model_num, force_cpu):
        self.model_file = "esrgan.py"
        self.name = _model_list[model_num]
        gfu.gimp.progress_init("Running {}...".format(self.name))
        result = self.predict(self.drawable, self.name, force_cpu=force_cpu)
        if not result:
           return
        h, w, _ = result.shape
        self.gimp_img.resize(w, h, 0, 0)
        self.create_layer(
            result, name=self.drawable.name + ": " + self.name
        )


_model_list = [
    'RealESRGAN_x4plus',
    'RealESRNet_x4plus',
    'RealESRGAN_x4plus_anime_6B',
    'RealESRGAN_x2plus',
    'realesr-animevideov3',
    'realesr-general-wdn-x4v3',
    'realesr-general-x4v3',
]

plugin = ESRGAN()
plugin.register(
    proc_name="esrgan",
    blurb="Real-ESRGAN\nSuper Resolution",
    help="https://github.com/xinntao/Real-ESRGAN",
    author="yantoz",
    copyright="",
    date="2023",
    label="Super Resolution (Real-ESRGAN) ...",
    imagetypes="RGB*",
    params=[
        (gfu.PF_OPTION, "Model",     "Choose model:", 0,       _model_list),
        (gfu.PF_BOOL,   "force_cpu", "Force CPU",     False),
    ],
)
