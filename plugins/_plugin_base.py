from __future__ import print_function, absolute_import, division

import os
import subprocess
import sys
import xmlrpclib
import threading
import traceback
from SimpleXMLRPCServer import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from abc import ABCMeta, abstractmethod

#import gtk
import time

import gimpfu as gfu
from gimpfu import gimp, pdb

from _config import python3_executable, torch_home

base_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
models_dir = os.path.join(base_dir, 'models')

import logging

#logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("plugin_base")


class GimpPluginBase(object):
    __metaclass__ = ABCMeta

    def __init__(self):
        self.model_file = None
        self.gimp_img = None
        self.drawable = None
        self.name = None
        self._model_proxy = None

    @abstractmethod
    def run(self, *args, **kwargs):
        # example
        self.model_file = 'xyz.py'
        result = self.predict(self.drawable)
        self.create_layer(result)

    def create_layer(self, result, name=None):
        name = name or self.drawable.name + ' ' + self.name
        return imgarray_to_layer(result, self.gimp_img, name)

    def create_image(self, result, name=None):
        name = name or self.drawable.name + ' ' + self.name
        return imgarray_to_image(result, name)

    def register(self, proc_name, blurb, help, author, copyright, date, label,
                 imagetypes, params=None, results=None, menu="<Image>/Layer/GIMP-ML-Hub",
                 domain=None, on_query=None, on_run=None):
        self.name = proc_name
        gfu.register(
            proc_name,
            blurb,
            help,
            author,
            copyright,
            date,
            label,
            imagetypes,
            params=[(gfu.PF_IMAGE, "image", "Input image", None),
                    (gfu.PF_DRAWABLE, "drawable", "Input drawable", None)]
                   + (params or []),
            results=results or [],
            function=self.run_outer,
            menu=menu,
            domain=domain, on_query=on_query, on_run=on_run
        )
        gimp.main(None, None, gfu._query, self._run)

    def run_outer(self, gimp_img, drawable, *extra_args):
        self.gimp_img = gimp_img
        self.drawable = drawable
        print("Running {}...".format(self.name))
        pdb.gimp_image_undo_group_start(self.gimp_img)
        gimp.progress_init("Running {}...".format(self.name))
        self.run(*extra_args)
        pdb.gimp_image_undo_group_end(self.gimp_img)

    def predict(self, *args, **kwargs):
        assert self.model_file is not None
        self._model_proxy = ModelProxy(self.model_file)
        if kwargs.get("force_cpu") is None:
            kwargs["force_cpu"] = False
        try:
            result = self._model_proxy(*args, **kwargs)
            self._model_proxy = None
            return result
        except:
            error_info = self._format_error(traceback.format_exc())
            gimp.message(error_info)
            raise

    def _format_error(self, formatted_exception):
        exception_msg = formatted_exception.rstrip().splitlines()[-1]
        if "CUDA out of memory" in exception_msg:
            return ("Not enough GPU memory available to run the model with given input image size. "
                    "Try reducing the input layer's dimensions.\n\n" + exception_msg)
        return formatted_exception

    def kill(self):
        if self._model_proxy:
            self._model_proxy.kill()

    def _interrupt(self):
        self.kill()

    def _interact(self, proc_name, start_params):
        (blurb, help, author, copyright, date,
         label, imagetypes, plugin_type,
         params, results, function, menu, domain,
         on_query, on_run, has_run_mode) = gfu._registered_plugins_[proc_name]

        def run_script(run_params):
            params = start_params + tuple(run_params)
            gfu._set_defaults(proc_name, params)
            return apply(function, params)

        params = params[len(start_params):]

        # short circuit for no parameters ...
        if len(params) == 0:
             return run_script([])

        import pygtk
        pygtk.require('2.0')

        import gimpui
        import gtk
#       import pango
        gimpui.gimp_ui_init ()

        defaults = gfu._get_defaults(proc_name)
        defaults = defaults[len(start_params):]

        class EntryValueError(Exception):
            pass

        def warning_dialog(parent, primary, secondary=None):
            dlg = gtk.MessageDialog(parent, gtk.DIALOG_DESTROY_WITH_PARENT,
                                            gtk.MESSAGE_WARNING, gtk.BUTTONS_CLOSE,
                                            primary)
            if secondary:
                dlg.format_secondary_text(secondary)
            dlg.run()
            dlg.destroy()

        def error_dialog(parent, proc_name):
            import sys, traceback

            exc_str = exc_only_str = gfu._("Missing exception information")

            try:
                etype, value, tb = sys.exc_info()
                exc_str = "".join(traceback.format_exception(etype, value, tb))
                exc_only_str = "".join(traceback.format_exception_only(etype, value))
            finally:
                etype = value = tb = None

            title = gfu._("An error occurred running %s") % proc_name
            dlg = gtk.MessageDialog(parent, gtk.DIALOG_DESTROY_WITH_PARENT,
                                            gtk.MESSAGE_ERROR, gtk.BUTTONS_CLOSE,
                                            title)
            dlg.format_secondary_text(exc_only_str)

            alignment = gtk.Alignment(0.0, 0.0, 1.0, 1.0)
            alignment.set_padding(0, 0, 12, 12)
            dlg.vbox.pack_start(alignment)
            alignment.show()

            expander = gtk.Expander(gfu._("_More Information"));
            expander.set_use_underline(True)
            expander.set_spacing(6)
            alignment.add(expander)
            expander.show()

            scrolled = gtk.ScrolledWindow()
            scrolled.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
            scrolled.set_size_request(-1, 200)
            expander.add(scrolled)
            scrolled.show()

            label = gtk.Label(exc_str)
            label.set_alignment(0.0, 0.0)
            label.set_padding(6, 6)
            label.set_selectable(True)
            scrolled.add_with_viewport(label)
            label.show()

            def response(widget, id):
                widget.destroy()

            dlg.connect("response", response)
            dlg.set_resizable(True)
            dlg.show()

        # define a mapping of param types to edit objects ...
        class StringEntry(gtk.Entry):
            def __init__(self, default=""):
                gtk.Entry.__init__(self)
                self.set_text(str(default))
                self.set_activates_default(True)

            def get_value(self):
                return self.get_text()

        class TextEntry(gtk.ScrolledWindow):
            def __init__ (self, default=""):
                gtk.ScrolledWindow.__init__(self)
                self.set_shadow_type(gtk.SHADOW_IN)

                self.set_policy(gtk.POLICY_AUTOMATIC, gtk.POLICY_AUTOMATIC)
                self.set_size_request(100, -1)

                self.view = gtk.TextView()
                self.add(self.view)
                self.view.show()

                self.buffer = self.view.get_buffer()

                self.set_value(str(default))

            def set_value(self, text):
                self.buffer.set_text(text)

            def get_value(self):
                return self.buffer.get_text(self.buffer.get_start_iter(),
                                            self.buffer.get_end_iter())

        class IntEntry(StringEntry):
            def get_value(self):
                try:
                    return int(self.get_text())
                except ValueError, e:
                    raise EntryValueError, e.args

        class FloatEntry(StringEntry):
            def get_value(self):
                try:
                    return float(self.get_text())
                except ValueError, e:
                    raise EntryValueError, e.args

#       class ArrayEntry(StringEntry):
#           def get_value(self):
#               return eval(self.get_text(), {}, {})

        def precision(step):
            # calculate a reasonable precision from a given step size
            if math.fabs(step) >= 1.0 or step == 0.0:
                digits = 0
            else:
                digits = abs(math.floor(math.log10(math.fabs(step))));
            if digits > 20:
                digits = 20
            return int(digits)

        class SliderEntry(gtk.HScale):
            # bounds is (upper, lower, step)
            def __init__(self, default=0, bounds=(0, 100, 5)):
                step = bounds[2]
                self.adj = gtk.Adjustment(default, bounds[0], bounds[1],
                                          step, 10 * step, 0)
                gtk.HScale.__init__(self, self.adj)
                self.set_digits(precision(step))

            def get_value(self):
                return self.adj.value

        class SpinnerEntry(gtk.SpinButton):
            # bounds is (upper, lower, step)
            def __init__(self, default=0, bounds=(0, 100, 5)):
                step = bounds[2]
                self.adj = gtk.Adjustment(default, bounds[0], bounds[1],
                                          step, 10 * step, 0)
                gtk.SpinButton.__init__(self, self.adj, step, precision(step))

        class ToggleEntry(gtk.ToggleButton):
            def __init__(self, default=0):
                gtk.ToggleButton.__init__(self)

                self.label = gtk.Label(gfu._("No"))
                self.add(self.label)
                self.label.show()

                self.connect("toggled", self.changed)

                self.set_active(default)

            def changed(self, tog):
                if tog.get_active():
                    self.label.set_text(gfu._("Yes"))
                else:
                    self.label.set_text(gfu._("No"))

            def get_value(self):
                return self.get_active()

        class RadioEntry(gtk.VBox):
            def __init__(self, default=0, items=((gfu._("Yes"), 1), (gfu._("No"), 0))):
                gtk.VBox.__init__(self, homogeneous=False, spacing=2)

                button = None

                for (label, value) in items:
                    button = gtk.RadioButton(button, label)
                    self.pack_start(button)
                    button.show()

                    button.connect("toggled", self.changed, value)

                    if value == default:
                        button.set_active(True)
                        self.active_value = value

            def changed(self, radio, value):
                if radio.get_active():
                    self.active_value = value

            def get_value(self):
                return self.active_value

        class ComboEntry(gtk.ComboBox):
            def __init__(self, default=0, items=()):
                store = gtk.ListStore(str)
                for item in items:
                    store.append([item])

                gtk.ComboBox.__init__(self, model=store)

                cell = gtk.CellRendererText()
                self.pack_start(cell)
                self.set_attributes(cell, text=0)

                self.set_active(default)

            def get_value(self):
                return self.get_active()

        def FileSelector(default="", title=None):
            # FIXME: should this be os.path.separator?  If not, perhaps explain why?
            if default and default.endswith("/"):
                if default == "/": default = ""
                return DirnameSelector(default)
            else:
                return FilenameSelector(default, title=title, save_mode=False)

        class FilenameSelector(gtk.HBox):
            #gimpfu.FileChooserButton
            def __init__(self, default, save_mode=True, title=None):
                super(FilenameSelector, self).__init__()
                if not title:
                    self.title = gfu._("Python-Fu File Selection")
                else:
                    self.title = title
                self.save_mode = save_mode
                box = self
                self.entry = gtk.Entry()
                image = gtk.Image()
                image.set_from_stock(gtk.STOCK_FILE, gtk.ICON_SIZE_BUTTON)
                self.button = gtk.Button()
                self.button.set_image(image)
                box.pack_start(self.entry)
                box.pack_start(self.button, expand=False)
                self.button.connect("clicked", self.pick_file)
                if default:
                    self.entry.set_text(default)

            def show(self):
                super(FilenameSelector, self).show()
                self.button.show()
                self.entry.show()

            def pick_file(self, widget):
                entry = self.entry
                dialog = gtk.FileChooserDialog(
                             title=self.title,
                             action=(gtk.FILE_CHOOSER_ACTION_SAVE
                                         if self.save_mode else
                                     gtk.FILE_CHOOSER_ACTION_OPEN),
                             buttons=(gtk.STOCK_CANCEL,
                                    gtk.RESPONSE_CANCEL,
                                    gtk.STOCK_SAVE
                                         if self.save_mode else
                                    gtk.STOCK_OPEN,
                                    gtk.RESPONSE_OK)
                            )
                dialog.set_alternative_button_order ((gtk.RESPONSE_OK, gtk.RESPONSE_CANCEL))
                dialog.show_all()
                response = dialog.run()
                if response == gtk.RESPONSE_OK:
                    entry.set_text(dialog.get_filename())
                dialog.destroy()

            def get_value(self):
                return self.entry.get_text()

        class DirnameSelector(gtk.FileChooserButton):
            def __init__(self, default=""):
                gtk.FileChooserButton.__init__(self,
                                               gfu._("Python-Fu Folder Selection"))
                self.set_action(gtk.FILE_CHOOSER_ACTION_SELECT_FOLDER)
                if default:
                    self.set_filename(default)

            def get_value(self):
                return self.get_filename()

        _edit_mapping = {
            gfu.PF_INT8        : IntEntry,
            gfu.PF_INT16       : IntEntry,
            gfu.PF_INT32       : IntEntry,
            gfu.PF_FLOAT       : FloatEntry,
            gfu.PF_STRING      : StringEntry,
#           gfu.PF_INT8ARRAY   : ArrayEntry,
#           gfu.PF_INT16ARRAY  : ArrayEntry,
#           gfu.PF_INT32ARRAY  : ArrayEntry,
#           gfu.PF_FLOATARRAY  : ArrayEntry,
#           gfu.PF_STRINGARRAY : ArrayEntry,
            gfu.PF_COLOR       : gimpui.ColorSelector,
            gfu.PF_ITEM        : IntEntry,  # should handle differently ...
            gfu.PF_IMAGE       : gimpui.ImageSelector,
            gfu.PF_LAYER       : gimpui.LayerSelector,
            gfu.PF_CHANNEL     : gimpui.ChannelSelector,
            gfu.PF_DRAWABLE    : gimpui.DrawableSelector,
            gfu.PF_VECTORS     : gimpui.VectorsSelector,

            gfu.PF_TOGGLE      : ToggleEntry,
            gfu.PF_SLIDER      : SliderEntry,
            gfu.PF_SPINNER     : SpinnerEntry,
            gfu.PF_RADIO       : RadioEntry,
            gfu.PF_OPTION      : ComboEntry,

            gfu.PF_FONT        : gimpui.FontSelector,
            gfu.PF_FILE        : FileSelector,
            gfu.PF_FILENAME    : FilenameSelector,
            gfu.PF_DIRNAME     : DirnameSelector,
            gfu.PF_BRUSH       : gimpui.BrushSelector,
            gfu.PF_PATTERN     : gimpui.PatternSelector,
            gfu.PF_GRADIENT    : gimpui.GradientSelector,
            gfu.PF_PALETTE     : gimpui.PaletteSelector,
            gfu.PF_TEXT        : TextEntry
        }

        if on_run:
            on_run()

        dialog = gimpui.Dialog(proc_name, "python-fu", None, 0, None, proc_name,
                               (gtk.STOCK_HELP, gtk.RESPONSE_HELP,
                                gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
                                gtk.STOCK_OK, gtk.RESPONSE_OK))

        dialog.set_alternative_button_order((gtk.RESPONSE_OK, gtk.RESPONSE_CANCEL))

        dialog.set_title("GIMP-ML-Hub")
        dialog.set_transient()

        vbox = gtk.VBox(False, 12)
        vbox.set_border_width(12)
        dialog.vbox.pack_start(vbox)
        vbox.show()

        if blurb:
            if domain:
                try:
                    (domain, locale_dir) = domain
                    trans = gettext.translation(domain, locale_dir, fallback=True)
                except ValueError:
                    trans = gettext.translation(domain, fallback=True)
                blurb = trans.ugettext(blurb)
            box = gimpui.HintBox(blurb)
            vbox.pack_start(box, expand=False)
            box.show()

        table = gtk.Table(len(params), 2, False)
        table.set_row_spacings(6)
        table.set_col_spacings(6)
        vbox.pack_start(table, expand=False)
        table.show()

        def response(dlg, id):
            if id == gtk.RESPONSE_OK:
                dlg.set_response_sensitive(gtk.RESPONSE_OK, False)
                #dlg.set_response_sensitive(gtk.RESPONSE_CANCEL, False)

                params = []

                try:
                    for wid in edit_wids:
                        params.append(wid.get_value())
                except EntryValueError:
                    warning_dialog(dialog, gfu._("Invalid input for '%s'") % wid.desc)
                else:
                    try:
                        dialog.res = run_script(params)
                    except gfu.CancelError:
                        pass
                    except Exception:
                        dlg.set_response_sensitive(gtk.RESPONSE_CANCEL, True)
                        error_dialog(dialog, proc_name)
                        raise
            elif id == gtk.RESPONSE_CANCEL:
                log.debug("Cancel request received")
                self._interrupt()
            elif id == gtk.RESPONSE_HELP:
                log.debug("Help requested")
                gtk.show_uri(None, help, gtk.gdk.CURRENT_TIME)
                return

            gtk.main_quit()

        dialog.connect("response", response)

        edit_wids = []
        for i in range(len(params)):
            pf_type = params[i][0]
            name = params[i][1]
            desc = params[i][2]
            def_val = defaults[i]

            label = gtk.Label(desc)
            label.set_use_underline(True)
            label.set_alignment(0.0, 0.5)
            table.attach(label, 1, 2, i, i+1, xoptions=gtk.FILL)
            label.show()

            # Remove accelerator markers from tooltips
            tooltip_text = desc.replace("_", "")

            if pf_type in (gfu.PF_SPINNER, gfu.PF_SLIDER, gfu.PF_RADIO, gfu.PF_OPTION):
                wid = _edit_mapping[pf_type](def_val, params[i][4])
            elif pf_type in (gfu.PF_FILE, gfu.PF_FILENAME):
                wid = _edit_mapping[pf_type](def_val, title= "%s - %s" %
                                              (proc_name, tooltip_text))
            else:
                wid = _edit_mapping[pf_type](def_val)


            label.set_mnemonic_widget(wid)

            table.attach(wid, 2,3, i,i+1, yoptions=0)

            if pf_type != gfu.PF_TEXT:
                wid.set_tooltip_text(tooltip_text)
            else:
                # Attach tip to TextView, not to ScrolledWindow
                wid.view.set_tooltip_text(tooltip_text)
            wid.show()

            wid.desc = desc
            edit_wids.append(wid)

        progress_vbox = gtk.VBox(False, 6)
        vbox.pack_end(progress_vbox, expand=False)
        progress_vbox.show()

        progress = gimpui.ProgressBar()
        progress_vbox.pack_start(progress)
        progress.show()

#       progress_label = gtk.Label()
#       progress_label.set_alignment(0.0, 0.5)
#       progress_label.set_ellipsize(pango.ELLIPSIZE_MIDDLE)

#       attrs = pango.AttrList()
#       attrs.insert(pango.AttrStyle(pango.STYLE_ITALIC, 0, -1))
#       progress_label.set_attributes(attrs)

#       progress_vbox.pack_start(progress_label)
#       progress_label.show()

        self._dialog = dialog

        dialog.show()
        dialog.set_keep_above(True)

        gtk.main()

        if hasattr(dialog, "res"):
            res = dialog.res
            dialog.destroy()
            return res
        else:
            dialog.destroy()
            raise gfu.CancelError

    def _run(self, proc_name, params):
        run_mode = params[0]
        func = gfu._registered_plugins_[proc_name][10]

        if run_mode == gfu.RUN_NONINTERACTIVE:
            return apply(func, params[1:])

        script_params = gfu._registered_plugins_[proc_name][8]

        min_args = 0
        if len(params) > 1:
            for i in range(1, len(params)):
                param_type = gfu._obj_mapping[script_params[i - 1][0]]
                if not isinstance(params[i], param_type):
                   break

            min_args = i

        if len(script_params) > min_args:
            start_params = params[:min_args + 1]

            if run_mode == gfu.RUN_WITH_LAST_VALS:
                default_params = gfu._get_defaults(proc_name)
                params = start_params + default_params[min_args:]
            else:
                params = start_params
        else:
            run_mode = gfu.RUN_NONINTERACTIVE

        if run_mode == gfu.RUN_INTERACTIVE:
            try:
                res = self._interact(proc_name, params[1:])
            except gfu.CancelError:
                return
            finally:
                try:
                    self._dialog.destroy()
                except:
                    pass
        else:
            res = apply(func, params[1:])

        gimp.displays_flush()

        return res


class ModelProxy(object):
    """
    When called, runs
        python3 models/<model_file>
    and waits for the subprocess to call get_args() and then return_result() or raise_error() over XML-RPC.
    Additionally, progress info can be reported via update_progress().
    """

    def __init__(self, model_file):
        self.python_executable = python3_executable
        self.model_path = os.path.join(models_dir, model_file)
        self.killswitch = threading.Event()
        self.server = None
        self.args = None
        self.kwargs = None
        self.result = None

    @staticmethod
    def _encode(x):
        if isinstance(x, gimp.Layer) or isinstance(x, gimp.Channel):
            x = layer_to_imgarray(x)
        if isinstance(x, ImgArray):
            x = x.encode()
        return x

    @staticmethod
    def _decode(x):
        if isinstance(x, list) and len(x) == 3 and x[0] == 'ImgArray':
            x = ImgArray.decode(x)
        return x

    def _rpc_get_args(self):
        assert isinstance(self.args, (list, tuple))
        assert isinstance(self.kwargs, dict)
        args = [self._encode(arg) for arg in self.args]
        kwargs = {k: self._encode(v) for k, v in self.kwargs.items()}
        return args, kwargs

    def _rpc_return_result(self, result):
        assert isinstance(result, (list, tuple))
        self.result = tuple(self._decode(x) for x in result)
        threading.Thread(target=lambda: self.server.shutdown()).start()

    def _rpc_raise_exception(self, exc_string):
        self.server.exception = exc_string
        threading.Thread(target=lambda: self.server.shutdown()).start()

    def _rpc_heartbeat(self):
        import gtk
        while gtk.events_pending():
            gtk.main_iteration()

    def _add_conda_env_to_path(self):
        env = os.environ.copy()
        conda_root = os.path.dirname(self.python_executable)
        env['PATH'] = os.pathsep.join([
            conda_root,
            os.path.join(conda_root, 'Library', 'mingw-w64', 'bin'),
            os.path.join(conda_root, 'Library', 'usr', 'bin'),
            os.path.join(conda_root, 'Library', 'bin'),
            os.path.join(conda_root, 'Scripts'),
            os.path.join(conda_root, 'bin'),
            env['PATH']
        ])
        return env

    def _start_subprocess(self, rpc_port, killswitch):
        env = self._add_conda_env_to_path()
        # make sure GIMP's Python 2 modules are not on PYTHONPATH
        if 'PYTHONPATH' in env:
            del env['PYTHONPATH']
        if 'PYTHONHOME' in env:
            del env['PYTHONHOME']
        env['TORCH_HOME'] = torch_home
        try:
            self.proc = subprocess.Popen([
                self.python_executable,
                self.model_path,
                'http://127.0.0.1:{}/'.format(rpc_port)
            ], env=env)
            while True:
                if killswitch.is_set():
                    self.proc.kill()
                    log.debug("subprocess killed")
                    break
                else:
                    if self.proc.poll() is None:
                        time.sleep(1)
                    else:
                        log.debug("subprocess done: {}".format(self.proc.returncode))
                        break
        finally:
            self.server.shutdown()
            self.server.server_close()

    def _init_rpc_server(self):
        # For cleaner exception info
        class RequestHandler(SimpleXMLRPCRequestHandler):
            def _dispatch(self, method, params):
                try:
                    return self.server.funcs[method](*params)
                except:
                    self.server.exception = sys.exc_info()
                    raise

        self.server = SimpleXMLRPCServer(('127.0.0.1', 0), allow_none=True, logRequests=False,
                                         requestHandler=RequestHandler)
        self.server.register_function(self._rpc_get_args, 'get_args')
        self.server.register_function(self._rpc_return_result, 'return_result')
        self.server.register_function(self._rpc_raise_exception, 'raise_exception')
        self.server.register_function(self._rpc_heartbeat, 'heartbeat')
        self.server.register_function(update_progress)
        self.server.exception = None
        rpc_port = self.server.server_address[1]
        return rpc_port

    def kill(self):
        self.killswitch.set()

    def __call__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

        rpc_port = self._init_rpc_server()
        self.killswitch.clear()
        t = threading.Thread(target=self._start_subprocess, args=(rpc_port,self.killswitch,))
        t.start()
        self.server.serve_forever()

        if self.result is None and not self.killswitch.is_set():
            if self.server.exception:
                if isinstance(self.server.exception, str):
                    raise RuntimeError(self.server.exception)
                type, value, traceback = self.server.exception
                raise type, value, traceback
            raise RuntimeError("Model did not return a result!")

        if self.result and len(self.result) == 1:
            return self.result[0]
        return self.result


class ImgArray(object):
    """Minimal Numpy ndarray-like object for serialization in RPC."""

    def __init__(self, buffer, shape):
        self.buffer = buffer
        self.shape = shape

    def encode(self):
        data = xmlrpclib.Binary(self.buffer)
        return "ImgArray", data, self.shape

    @staticmethod
    def decode(x):
        data, shape = x[1:]
        data = data.data
        return ImgArray(data, shape)


image_type_map = {
    1: gfu.GRAY_IMAGE,
    2: gfu.GRAYA_IMAGE,
    3: gfu.RGB_IMAGE,
    4: gfu.RGBA_IMAGE,
}

image_base_type_map = {
    1: gfu.GRAY,
    2: gfu.GRAY,
    3: gfu.RGB,
    4: gfu.RGB,
}


def layer_to_imgarray(layer):
    region = layer.get_pixel_rgn(0, 0, layer.width, layer.height)
    pixChars = region[:, :]  # Take whole layer
    return ImgArray(pixChars, (layer.height, layer.width, region.bpp))


def imgarray_to_layer(array, gimp_img, name):
    h, w, d = array.shape
    layer = gimp.Layer(gimp_img, name, w, h, image_type_map[d])
    region = layer.get_pixel_rgn(0, 0, w, h)
    region[:, :] = array.buffer
    gimp_img.insert_layer(layer, position=0)
    return layer


def imgarray_to_image(array, name):
    h, w, d = array.shape
    img = gimp.Image(w, h, image_base_type_map[d])
    imgarray_to_layer(array, img, name)
    gimp.Display(img)
    gimp.displays_flush()


def update_progress(percent, message):
    if percent is not None:
        pdb.gimp_progress_update(percent)
    else:
        pdb.gimp_progress_pulse()
    pdb.gimp_progress_set_text(message)
