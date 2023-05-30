import sys
import torch
import numpy as np
from _model_base import ModelBase


class LamaInpaint(ModelBase):
    def __init__(self):
        super().__init__()
        self.hub_repo = 'yantoz/lama'

    def load_model(self):
        model = torch.hub.load(self.hub_repo, 'lama', map_location=self.device)
        return model

    def predict(self, input_image, mask=None):

        h, w, d = input_image.shape
        assert d == 3, "Input image must be RGB"

        hm, wm, dm = mask.shape
        assert (hm == h) and (wm == w), "Mask must have same size with image"
        assert dm == 1, "Mask must be a greyscale channel"
        
        mask = np.squeeze(mask, axis=2)

        return self.model(input_image, mask)


model = LamaInpaint()

if __name__ == '__main__':
    rpc_url = sys.argv[1]
    model.process_rpc(rpc_url)
