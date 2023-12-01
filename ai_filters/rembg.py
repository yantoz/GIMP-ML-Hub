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
            [Type.OPTION, "model",          "Model",              0,                 self.model_list],
            [Type.BOOL,   "mask",           "Generate Mask",      True                              ],
            [Type.BOOL,   "alpha_matting",  "Alpha Matting",      False                             ],
            [Type.RANGE,  "thresholds",     "  - Thresholds",     [10,240],          (0,255)        ],
            [Type.SLIDER, "erode_size",     "  - Erosion Size",   10,                (0,255)        ],
            [Type.BOOL,   "force_cpu",      "Force CPU",          False                             ],
        ]

        super().__init__(parent, title, name, info, params)


    def run(self, img, bounds):

        params = self.params
        model = params["model"]
        mask = params["mask"]
        alpha_matting = params["alpha_matting"]
        thresholds = params["thresholds"]
        erode_size = params["erode_size"]
        self._force_cpu = params["force_cpu"]

        """
            alpha_matting (bool, optional): Flag indicating whether to use alpha matting. Defaults to False.
            alpha_matting_foreground_threshold (int, optional): Foreground threshold for alpha matting. Defaults to 240.
            alpha_matting_background_threshold (int, optional): Background threshold for alpha matting. Defaults to 10.
            alpha_matting_erode_size (int, optional): Erosion size for alpha matting. Defaults to 10.
        """
        alpha_matting_background_threshold = int(thresholds[0])
        alpha_matting_foreground_threshold = int(thresholds[1])
        alpha_matting_erode_size = int(erode_size)

        self.model_file = "RemBg.py"
        model_name = self.model_list[model][1]
        result = self.predict(img, mask, model=model_name,
            alpha_matting=alpha_matting, alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
            alpha_matting_background_threshold=alpha_matting_background_threshold, alpha_matting_erode_size=alpha_matting_erode_size)

        if result:
            layer = self.create_layer(result, mask=mask, reposition=True)
            self.message()
