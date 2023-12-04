#!/usr/bin/env python2
import sys
from os.path import dirname, realpath

sys.path.append(realpath(dirname(__file__)))
import gimpfu as gfu
from _plugin_base import GimpPluginBase


class SemanticSegmentation(GimpPluginBase):
    def run(self, model_num, force_cpu):
        self.model_file = "DeepLabV3.py"
        self.name = _model_list[model_num][0]
        gfu.gimp.progress_init("Running {}...".format(self.name))
        result = self.predict(self.drawable, _model_list[model_num], force_cpu=force_cpu)
        if not result:
            return
        self.create_layer(
            result, name=self.drawable.name + ":" + _model_list[model_num][0]
        )


_model_list = [
    ("Deeplab 3+ Resnet 101", "deeplabv3plus_resnet101"),
    ("Deeplab 3+ Resnet 50", "deeplabv3plus_resnet50"),
    ("Deeplab 3+ Mobilenet", "deeplabv3plus_mobilenet"),
    ("Deeplab 3 Resnet 101", "deeplabv3_resnet101"),
    ("Deeplab 3 Resnet 50", "deeplabv3_resnet50"),
    ("Deeplab 3 Mobilenet", "deeplabv3_mobilenet"),
]

_model_params = (name for i, (name, model) in enumerate(_model_list))

plugin = SemanticSegmentation()
plugin.register(
    proc_name="semanticsegmentation",
    blurb="DeepLabV3Plus\nSemantic segmentation map based on deep learning",
    help="https://github.com/joemarshall/DeepLabV3Plus-Pytorch",
    author="Joe Marshall",
    copyright="",
    date="2020",
    label="Semantic Segmentation (DeepLabV3) ...",
    imagetypes="RGB*",
    params=[
        (gfu.PF_OPTION, "Model",     "Choose model:", 0,       _model_params),
        (gfu.PF_BOOL,   "force_cpu", "Force CPU",     False),
    ],
)
