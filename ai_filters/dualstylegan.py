from ._filter_base import Type, FilterBase

class DualStyleGAN(FilterBase):

    def __init__(self, parent):

        title = "Style Transfer (DualStyleGAN)"
        name = "DualStyleGAN"
        info = "https://github.com/williamyang1991/DualStyleGAN/tree/main/doc_images"

        self.style_list = [
            ("Arcane",      "arcane"),
            ("Anime",       "anime"),
            ("Caricature",  "caricature"),
            ("Cartoon",     "cartoon"),
            ("Comic",       "comic"),
            ("Pixar",       "pixar"),
            ("Slamdunk",    "slamdunk"),
        ]

        params = [
            [Type.OPTION, "style",          "Style",          0,     self.style_list],
            [Type.INT,    "style_id",       "Style ID",       26                    ],
            [Type.FLOAT,  "style_degree",   "Style Degree",   0.5                   ],
            [Type.BOOL,   "color_transfer", "Color Transfer", False                 ],
            [Type.BOOL,   "keep_size",      "Keep Size",      True                  ],
        ]

        super().__init__(parent, title, name, info, params)


    def run(self, img, bounds):

        params = self.params
        style_num = params["style"]
        style_id = params["style_id"]
        style_degree = params["style_degree"]
        color_transfer = params["color_transfer"]
        keep_size = params["keep_size"]

        self.model_file = "DualStyleGAN.py"
        name = self.style_list[style_num][0]
        result = self.predict(img, self.style_list[style_num][1], style_id, style_degree, color_transfer, keep_size)
        layer = self.create_layer(result, reposition=True)
