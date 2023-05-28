import sys
import torch

from _tiled_model_base import TiledModelBase

import logging

#logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("tiled_model_base")


class ESRGAN(TiledModelBase):
    def __init__(self):
        super().__init__()
        self.hub_repo = 'yantoz/Real-ESRGAN'
        self.network = None

    def load_model(self):
        model = torch.hub.load(self.hub_repo, 'ESRGAN', map_location=self.device, network=self.network)
        return model

    def preProcess(self, image):
        # input is numpy (h, w, c) [0..255]
        # output is torch (b, c, h, w) [0..1]
        return torch.from_numpy(image.copy()).permute(2, 0, 1).float().div(255).unsqueeze(0).to(self.device)

    def postProcess(self, image):
        # input is torch (b, c, h, w) [0..1]
        # output is numpy (h, w, c) [0..255]
        return image.squeeze().permute(1, 2, 0).clamp(0, 1).mul(255).byte().cpu().numpy()

    def predict(self, input_image, network):
        self.network = network
        log.debug("Input: {}".format(input_image.shape))
        log.debug("Network: {} (x{})".format(network, self.model.scale))
        output = self.processImageTiled(input_image, scale=self.model.scale, TILE_SIZE=256, TILE_PAD=10)
        log.debug("Output: {}".format(output.shape))
        return output

model = ESRGAN()

if __name__ == '__main__':
    rpc_url = sys.argv[1]
    model.process_rpc(rpc_url)
