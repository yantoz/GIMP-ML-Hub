import sys
import torch

from _tiled_model_base import TiledModelBase


class SRResNet(TiledModelBase):
    def __init__(self):
        super().__init__()
        self.hub_repo = 'valgur/pytorch-SRResNet'

    def load_model(self):
        model = torch.hub.load(self.hub_repo, 'SRResNet', pretrained=True, map_location=self.device)
        model.to(self.device)
        return model

    def preProcess(self, image):
        # input is numpy (h, w, c) [0..255]
        # output is torch (b, c, h, w) [0..1]
        return torch.from_numpy(image.copy()).permute(2, 0, 1).float().div(255).unsqueeze(0).to(self.device)

    def postProcess(self, image):
        # input is torch (b, c, h, w) [0..1]
        # output is numpy (h, w, c) [0..255]
        return image.squeeze().permute(1, 2, 0).clamp(0, 1).mul(255).byte().cpu().numpy()

    def predict(self, input_image):
        return self.processImageTiled(input_image, scale=4, TILE_SIZE=256, TILE_PAD=10)


model = SRResNet()

if __name__ == '__main__':
    rpc_url = sys.argv[1]
    model.process_rpc(rpc_url)
