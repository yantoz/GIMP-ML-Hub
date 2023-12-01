from ._filter_base import Type, FilterBase

class SAM(FilterBase):

    def __init__(self, parent):

        title = "Segment Anything (sam)"
        name = "Segment Anything"
        info = "https://github.com/facebookresearch/segment-anything"

        params = [
            [Type.RADIO,  "type",           "Type",                      1,                 ("Point","Box")],
            [Type.BOOL,   "mask",           "Generate Mask",             True                              ],
            [Type.BOOL,   "alpha_matting",  "Alpha Matting",             False                             ],
            [Type.RANGE,  "thresholds",     "  - Thresholds",            [10,240],          (0,255)        ],
            [Type.SLIDER, "erode_size",     "  - Erosion Size",          10,                (0,255)        ],
            [Type.BOOL,   "force_cpu",      "Force CPU",                 False                             ],
        ]

        super().__init__(parent, title, name, info, params)


    def run(self, img, bounds):

        params = self.params
        model = "sam"
        type = params["type"]
        alpha_matting = params["alpha_matting"]
        thresholds = params["thresholds"]
        erode_size = params["erode_size"]
        mask = params["mask"]
        self._force_cpu = params["force_cpu"]

        doc = self.activeDocument
        selection = doc.selection()

        # get selection mask values (0..255)
        #seldata = selection.pixelData(0, 0, doc.width(), doc.height())

        if not selection:
            self.message("Selection was empty!")
            return

        if type == 0:
            sam_prompt = [{
                "type": "point",
                "data": [int((2*selection.x()+selection.width())/2),int((2*selection.y()+selection.height())/2)],
                "label": 1,
            }]
        else:
            sam_prompt = [{
                "type": "rectangle",
                "data": [selection.x(),selection.y(),selection.x()+selection.width(),selection.y()+selection.height()],
            }]
        print(sam_prompt)

        """
            alpha_matting (bool, optional): Flag indicating whether to use alpha matting. Defaults to False.
            alpha_matting_foreground_threshold (int, optional): Foreground threshold for alpha matting. Defaults to 240.
            alpha_matting_background_threshold (int, optional): Background threshold for alpha matting. Defaults to 10.
            alpha_matting_erode_size (int, optional): Erosion size for alpha matting. Defaults to 10.
        """
        alpha_matting_background_threshold = int(thresholds[0])
        alpha_matting_foreground_threshold = int(thresholds[1])
        alpha_matting_erode_size = int(erode_size)

        self.model_file = "SAM.py"
        result = self.predict(img, model="sam", sam_prompt=sam_prompt,
            alpha_matting=alpha_matting, alpha_matting_foreground_threshold=alpha_matting_foreground_threshold,
            alpha_matting_background_threshold=alpha_matting_background_threshold, alpha_matting_erode_size=alpha_matting_erode_size)

        if result:
            doc.setSelection(None)
            layer = self.create_layer(result, mask=mask, reposition=True)
            self.message()
