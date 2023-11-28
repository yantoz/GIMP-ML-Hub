from ._filter_base import Type, FilterBase

class SemanticSegmentation(FilterBase):

    def __init__(self, parent):

        title = "Semantic Segmentation (DeepLabV3)"
        name = "Semantic Segmentation"
        info = "https://github.com/joemarshall/DeepLabV3Plus-Pytorch"

        self.model_list = [
            ("Deeplab 3+ Resnet 101", "deeplabv3plus_resnet101"),
            ("Deeplab 3+ Resnet 50", "deeplabv3plus_resnet50"),
            ("Deeplab 3+ Mobilenet", "deeplabv3plus_mobilenet"),
            ("Deeplab 3 Resnet 101", "deeplabv3_resnet101"),
            ("Deeplab 3 Resnet 50", "deeplabv3_resnet50"),
            ("Deeplab 3 Mobilenet", "deeplabv3_mobilenet"),
        ]

        params = [
            [Type.OPTION, "model",          "Model",          0,     self.model_list],
        ]

        super().__init__(parent, title, name, info, params)


    def run(self, img, bounds):

        params = self.params
        model_num = params["model"]

        self.model_file = "DeepLabV3.py"
        name = self.model_list[model_num][0]
        result = self.predict(img, self.model_list[model_num])
        layer = self.create_layer(result, reposition=True)
