from ._filter_base import Type, FilterBase

class ESRGAN(FilterBase):

    def __init__(self, parent):

        title = "Super Resolution (Real-ESRGAN)"
        name = "Real-ESRGAN"
        info = "https://github.com/xinntao/Real-ESRGAN"

        self.model_list = [
            'RealESRGAN_x4plus',
            'RealESRNet_x4plus',
            'RealESRGAN_x4plus_anime_6B',
            'RealESRGAN_x2plus',
            'realesr-animevideov3',
            'realesr-general-wdn-x4v3',
            'realesr-general-x4v3',
        ]

        params = [
            [Type.OPTION, "model",          "Model",          0,     self.model_list],
        ]

        super().__init__(parent, title, name, info, params)


    def run(self, img, bounds):

        params = self.params
        model_num = params["model"]

        self.model_file = "esrgan.py"
        name = self.model_list[model_num]
        result = self.predict(img, name)
        doc = self.create_image(result)
