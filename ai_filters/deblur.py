from ._filter_base import Type, FilterBase

class Deblur(FilterBase):

    def __init__(self, parent):

        title = "Deblur (DeblurGANv2)"
        name = "Deblur"
        info = "https://github.com/VITA-Group/DeblurGANv2"

        params = [
            [Type.BOOL,   "force_cpu",      "Force CPU",      False                 ],
        ]

        super().__init__(parent, title, name, info, params)


    def run(self, img, bounds):

        params = self.params
        self._force_cpu = params["force_cpu"]

        self.model_file = "DeblurGANv2.py"
        result = self.predict(img)
        if result:
            layer = self.create_layer(result, reposition=True)
            self.message()
