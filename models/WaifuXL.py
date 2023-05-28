import sys
import torch
import numpy as np

from _tiled_model_base import TiledModelBase


class WaifuXL(TiledModelBase):
    def __init__(self):
        super().__init__()
        self.hub_repo = 'yantoz/WaifuXL'

    def load_model(self):
        model = torch.hub.load(self.hub_repo, 'WaifuXL')
        return model

    def predict(self, input_image):
        return self.processImageTiled(input_image, scale=2, TILE_SIZE=1024, TILE_PAD=10)


model = WaifuXL()

if __name__ == '__main__':
    rpc_url = sys.argv[1]
    model.process_rpc(rpc_url)
