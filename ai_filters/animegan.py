from ._filter_base import Type, FilterBase

class AnimeGAN(FilterBase):

    def __init__(self, parent):

        title = "Photo to Anime (AnimeGANv3)"
        name = "AnimeGANv3"
        info = "https://github.com/TachibanaYoshino/AnimeGANv3"

        self.model_list = [
            ("v3 Hayao",            "v3hayao"),
            ("v3 JP Face",          "v3jpface"),
            ("v3 Portrait Sketch",  "v3portraitsketch"),
            ("v2 Hayao",            "v2hayao"),
            ("v2 Paprika",          "v2paprika"),
            ("v2 Shinkai",          "v2shinkai"),
        ]

        params = [
            [Type.OPTION, "model",          "Model",          0,     self.model_list],
            [Type.BOOL,   "force_cpu",      "Force CPU",      False                 ],
        ]

        super().__init__(parent, title, name, info, params)


    def run(self, img, bounds):

        params = self.params
        model = params["model"]
        self._force_cpu = params["force_cpu"]

        self.model_file = "AnimeGAN.py"
        result = self.predict(img, self.model_list[model][1])
        if result:
            layer = self.create_layer(result, reposition=True)
            self.message()
