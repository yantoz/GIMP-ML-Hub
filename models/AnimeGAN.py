import sys
import torch
import numpy as np

from _model_base import ModelBase, handle_alpha

class AnimeGAN(ModelBase):
    def __init__(self):
        super().__init__()
        self.hub_repo = 'yantoz/AnimeGANv3'

    def load_model(self):
        model = torch.hub.load(self.hub_repo, 'animegan', id=self.id, map_location=self.device)
        return model

    @handle_alpha
    def predict(self, input_image, id, **kwargs):
        self.id = id
        output = self.model(input_image)
        return output

model = AnimeGAN()

if __name__ == '__main__':
    rpc_url = sys.argv[1]
    model.process_rpc(rpc_url)
