import sys
import time
from os.path import dirname, realpath

sys.path.append(realpath(dirname(__file__)))
import gimpfu as gfu
from _plugin_base import GimpPluginBase

class SemanticSegmentation(GimpPluginBase):
    def run(self,modelNum):
        self.model_file = 'semanticsegmentation.py'
        self.name=modelList[modelNum][0]
        gfu.gimp.progress_init("Running {}...".format(self.name))
        result = self.predict(self.drawable,modelList[modelNum])
        self.create_layer(result,name=self.drawable.name+":"+modelList[modelNum][0])


modelList=[("Deeplab 3+ Resnet 101", "deeplabv3plus_resnet101"),
                 ( "Deeplab 3+ Resnet 50", "deeplabv3plus_resnet50"),
                 ( "Deeplab 3+ Mobilenet", "deeplabv3plus_mobilenet"),
                 ("Deeplab 3 Resnet 101", "deeplabv3_resnet101"),
                 ( "Deeplab 3 Resnet 50", "deeplabv3_resnet50"),
                 ( "Deeplab 3 Mobilenet", "deeplabv3_mobilenet")]
                 
modelParams=(name for i,(name,model) in enumerate(modelList))

plugin = SemanticSegmentation()
plugin.register(
    proc_name="semanticsegmentation",
    blurb="semanticsegmentation",
    help="Generate semantic segmentation map based on deep learning.",
    author="Joe Marshall",
    copyright="",
    date="2020",
    label="Semantic segmentation...",
    imagetypes="RGB*",
    params=[
        (gfu.PF_OPTION, "Model", "Choose model:", 0,modelParams)
    ]
)
gfu.main()
