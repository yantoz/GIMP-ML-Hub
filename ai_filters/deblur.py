from ._filter_base import Type, FilterBase

class Deblur(FilterBase):

    def __init__(self, parent):

        title = "Deblur (DeblurGANv2)"
        name = "Deblur"
        info = "https://github.com/VITA-Group/DeblurGANv2"

        params = []

        super().__init__(parent, title, name, info, params)


    def run(self, img, bounds):
        self.model_file = "DeblurGANv2.py"
        result = self.predict(img)
        layer = self.create_layer(result, reposition=True)
