#!/usr/bin/python

import traceback
from gimpfu import pdb, gimp
import gimpfu as gfu

infile = "test.jpg"
outfile = "out.png"
try:
    image = pdb.gimp_file_load(infile, infile, run_mode=gfu.RUN_NONINTERACTIVE)
    # w = 200
    # h = round(w * image.height / float(image.width))
    # pdb.gimp_image_scale(image, w, h)
    pdb.python_fu_super_resolution(image, image.active_layer)
    image.flatten()
    pdb.gimp_file_save(image, image.active_layer, outfile, outfile, run_mode=gfu.RUN_NONINTERACTIVE)
except:
    gimp.message("ERROR:\n" + traceback.format_exc())
pdb.gimp_quit(1)
