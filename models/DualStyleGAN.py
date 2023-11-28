import os
import sys

import torch
import torch.hub

import cv2

from _model_base import ModelBase, handle_alpha

import logging

#logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("model")


class DualStyleGAN(ModelBase):
    def __init__(self):
        super().__init__()
        self.hub_repo = "yantoz/DualStyleGAN"

    def load_model(self):
        if self.device != "cuda":
            os.environ['CUDA_VISIBLE_DEVICES'] = ""
        model = torch.hub.load(self.hub_repo, 'dualstylegan',
            progress=True, map_location=self.device,
            style=self.style, style_id=self.style_id, style_degree=self.style_degree,
            color_transfer=self.color_transfer)
        return model

    @handle_alpha
    @torch.no_grad()
    def predict(self, input_image, style, style_id, style_degree, color_transfer, keep_size):
       
        self.style = style
        self.style_id = style_id
        self.style_degree = style_degree
        self.color_transfer = color_transfer

        h, w, d = input_image.shape
        assert d == 3, "Input image must be RGB"

        log.debug("Input: {}".format(input_image.shape))
        _, output = self.model(input_image)
        log.debug("Output: {}".format(output.shape))

        if keep_size:

           # resize keeping aspect ratio

           hh, ww, _ = output.shape
           if hh/h > ww/w:
               hh = int(hh*w/ww+0.5)
               ww = w
           else:
               ww = int(ww*h/hh+0.5)
               hh = h
           output = cv2.resize(output, (ww, hh))
           log.debug("Resized output: {}".format(output.shape))

           # crop extra

           if ww > w:
               s = int((ww-w)/2+0.5)
               output = output[:,s:(s+w),:]
           if hh > h:
               s = int((hh-h)/2+0.5)
               output = output[s:(s+h),:,:]

        return output

model = DualStyleGAN()

if __name__ == "__main__":
    rpc_url = sys.argv[1]
    model.process_rpc(rpc_url)
