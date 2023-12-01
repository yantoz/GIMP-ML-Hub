from ._filter_base import Type, FilterBase

class RemBg(FilterBase):

    def __init__(self, parent):

        title = "Remove Background (rembg)"
        name = "Remove Background"
        info = "https://github.com/danielgatis/rembg"

        self.model_list = [
            ("General Usecases",                  "u2net"),
            ("Lightweight, General",              "u2netp"),
            ("Human Segmentation",                "u2net_human_seg"),
            ("Cloths Parsing from Portrait",      "u2net_cloth_seg"),
            ("Image Segmentation, General",       "isnet-general-use"),
            ("Image Segmentation, Anime",         "isnet-anime"),
        ]

        params = [
            [Type.OPTION, "model",          "Model",          0,     self.model_list],
            [Type.BOOL,   "mask",           "Generate Mask",  True                  ],
            [Type.BOOL,   "force_cpu",      "Force CPU",      False                 ],
        ]

        super().__init__(parent, title, name, info, params)


    def run(self, img, bounds):

        params = self.params
        model = params["model"]
        mask = params["mask"]
        self._force_cpu = params["force_cpu"]

        self.model_file = "RemBg.py"
        model_name = self.model_list[model][1]
        result = self.predict(img, mask, model=model_name)
        if result:
            layer = self.create_layer(result, mask=mask, reposition=True)
            self.message()
