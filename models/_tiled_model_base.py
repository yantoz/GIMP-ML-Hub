import sys
import math

import torch
import numpy as np

from _model_base import ModelBase, handle_alpha

import logging

log = logging.getLogger("tiled_model_base")


class TiledModelBase(ModelBase):

    def __init__(self):
        super().__init__()

    def preProcess(self, image):
        # input is numpy (h, w, c) [0..255]
        return image

    def postProcess(self, image):
        # output is numpy (h, w, c) [0..255]
        return image

    @handle_alpha
    @torch.no_grad()
    def processImageTiled(self, input_image, scale, TILE_SIZE=256, TILE_PAD=10):

        def processTile(img, scale):

            # pad when necessary
            pad_h, pad_w = 0, 0
            h, w, _ = img.shape
            if (h % scale != 0):
                pad_h = (scale - h % scale)
            if (w % scale != 0):
                pad_w = (scale - w % scale)
            img = np.pad(img, ((0, pad_h), (0, pad_w), (0, 0)), 'reflect')

            im_input = self.preProcess(img)
            output = self.postProcess(self.model(im_input))

            # remove preadded pads
            oh, ow, _ = output.shape
            output = output[0:oh-pad_h*scale, 0:ow-pad_w*scale, :]

            return output


        height, width, depth = input_image.shape
        assert depth == 3, "Input image must be RGB"

        output_height = height * scale
        output_width = width * scale
        output_shape = (output_height, output_width, depth)

        # start with black image
        output = np.zeros(output_shape)
        tiles_x = math.ceil(width / TILE_SIZE)
        tiles_y = math.ceil(height / TILE_SIZE)

        ntiles = tiles_x * tiles_y

        # loop over all tiles
        for y in range(tiles_y):
            for x in range(tiles_x):
    
                n = y * tiles_x + x + 1
                self.update_progress(n/float(ntiles), "Processing tile {}/{}".format(n, ntiles))

                # extract tile from input image
                ofs_x = x * TILE_SIZE
                ofs_y = y * TILE_SIZE
                # input tile area on total image
                input_start_x = ofs_x
                input_end_x = min(ofs_x + TILE_SIZE, width)
                input_start_y = ofs_y
                input_end_y = min(ofs_y + TILE_SIZE, height)

                # input tile area on total image with padding
                input_start_x_pad = max(input_start_x - TILE_PAD, 0)
                input_end_x_pad = min(input_end_x + TILE_PAD, width)
                input_start_y_pad = max(input_start_y - TILE_PAD, 0)
                input_end_y_pad = min(input_end_y + TILE_PAD, height)

                # input tile dimensions
                input_tile_width = input_end_x - input_start_x
                input_tile_height = input_end_y - input_start_y
                tile_idx = y * tiles_x + x + 1
                input_tile = input_image[input_start_y_pad:input_end_y_pad, input_start_x_pad:input_end_x_pad, :]

                # process tile
                output_tile = processTile(input_tile, scale)

                # output tile area on total image
                output_start_x = input_start_x * scale
                output_end_x = input_end_x * scale
                output_start_y = input_start_y * scale
                output_end_y = input_end_y * scale

                # output tile area without padding
                output_start_x_tile = (input_start_x - input_start_x_pad) * scale
                output_end_x_tile = output_start_x_tile + input_tile_width * scale
                output_start_y_tile = (input_start_y - input_start_y_pad) * scale
                output_end_y_tile = output_start_y_tile + input_tile_height * scale

                # put tile into output image
                output[output_start_y:output_end_y, output_start_x:output_end_x,:] = \
                    output_tile[output_start_y_tile:output_end_y_tile, output_start_x_tile:output_end_x_tile,:]

        return output

