from ._filter_base import Type, FilterBase

class LamaInpaint(FilterBase):

    def __init__(self, parent):

        title = "Inpaint (Lama)"
        name = "Inpaint"
        info = "https://github.com/advimman/lama"

        params = [
            [Type.BOOL,   "force_cpu",      "Force CPU",      False                 ],
        ]

        super().__init__(parent, title, name, info, params)


    def run(self, img, bounds):

        params = self.params
        self._force_cpu = params["force_cpu"]

        self.model_file = "lama.py"
        result = self.predict(img)
        if result:
            layer = self.create_layer(result, reposition=True)
            self.message()
