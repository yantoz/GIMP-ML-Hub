import os
import sys
import numpy as np

import torch
import torch.hub

from _model_base import ModelBase

import logging

#logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("sam")


class SAM(ModelBase):

    def __init__(self):
        super().__init__()
        self.hub_repo = 'yantoz/rembg'

    def load_model(self):
        if self.device != "cuda":
            os.environ['CUDA_VISIBLE_DEVICES'] = ""
        model = torch.hub.load(self.hub_repo, 'RemBg', map_location=self.device)
        return model

    def predict(self, input_image, **kwargs):
        """
        Additional Parameters:
            alpha_matting (bool, optional): Flag indicating whether to use alpha matting. Defaults to False.
            alpha_matting_foreground_threshold (int, optional): Foreground threshold for alpha matting. Defaults to 240.
            alpha_matting_background_threshold (int, optional): Background threshold for alpha matting. Defaults to 10.
            alpha_matting_erode_size (int, optional): Erosion size for alpha matting. Defaults to 10.
            session (Optional[BaseSession], optional): A session object for the 'u2net' model. Defaults to None.
            only_mask (bool, optional): Flag indicating whether to return only the binary masks. Defaults to False.
            post_process_mask (bool, optional): Flag indicating whether to post-process the masks. Defaults to False.
            bgcolor (Optional[Tuple[int, int, int, int]], optional): Background color for the cutout image. Defaults to None.
        """
        output = self.model(input_image, mask=True, **kwargs)
        return output

model = SAM()

if __name__ == '__main__':
    rpc_url = sys.argv[1]
    model.process_rpc(rpc_url)
