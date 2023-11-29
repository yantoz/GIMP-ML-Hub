from ._filter_base import Type, FilterBase

class VToonify(FilterBase):

    def __init__(self, parent):

        title = "Style Transfer (vToonify)"
        name = "vToonify"
        info = "https://github.com/williamyang1991/DualStyleGAN/tree/main/doc_images"

        self.style_list = [
            ("Arcane",                    "arcane"),
            ("Caricature1 (s039,d0.5)",   "caricature1"),
            ("Caricature2 (s068,d0.5)",   "caricature2"),
            ("Cartoon",                   "cartoon"),
            ("Comic",                     "comic"),
            ("Illustration1 (s004)",      "illustration1"),
            ("Illustration2 (s009)",      "illustration2"),
            ("Illustration3 (s043)",      "illustration3"),
            ("Illustration4 (s054)",      "illustration4"),
            ("Illustration5 (s086)",      "illustration5"),
            ("Pixar",                     "pixar"),
        ]

        params = [
            [Type.OPTION, "style",          "Style",          0,     self.style_list],
            [Type.INT,    "style_id",       "Style ID",       26                    ],
            [Type.FLOAT,  "style_degree",   "Style Degree",   0.5                   ],
            [Type.BOOL,   "color_transfer", "Color Transfer", False                 ],
            [Type.BOOL,   "keep_size",      "Keep Size",      True                  ],
            [Type.BOOL,   "force_cpu",      "Force CPU",      False                 ],
        ]

        super().__init__(parent, title, name, info, params)


    def run(self, img, bounds):

        params = self.params
        style_num = params["style"]
        style_id = params["style_id"]
        style_degree = params["style_degree"]
        color_transfer = params["color_transfer"]
        keep_size = params["keep_size"]
        self._force_cpu = params["force_cpu"]

        self.model_file = "VToonify.py"
        name = self.style_list[style_num][0]
        result = self.predict(img, self.style_list[style_num][1], style_id, style_degree, color_transfer, keep_size)
        if result:
            layer = self.create_layer(result, reposition=True)
