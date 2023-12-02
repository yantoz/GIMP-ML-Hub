#!/usr/bin/env python2
import sys
import traceback

from os.path import dirname, realpath

sys.path.append(realpath(dirname(__file__)))
from gimpfu import main, gimp, pdb
from _plugin_base import GimpPluginBase


class LamaInpaint(GimpPluginBase):
    def run(self):
        try:
            self.model_file = 'lama.py'
            if not isinstance(self.drawable, gimp.Layer):
                raise RuntimeError("Select the layer, not mask, and re-run")
            layer = self.drawable
            mask = layer.mask
            if mask is None:
                raise RuntimeError("Add layer mask and mask region to inpaint")
        except:
            error_info = self._format_error(traceback.format_exc())
            gimp.message(error_info)
            raise
        result = self.predict(layer, mask=mask)
        if result:
            self.create_layer(result)


plugin = LamaInpaint()
plugin.register(
    proc_name="lama-inpaint",
    blurb="lama-inpaint",
    help="Inpaint masked area with Lama",
    author="yantoz",
    copyright="",
    date="2023",
    label="Inpaint (LaMa) ...",
    imagetypes="RGB*"
)
main()
