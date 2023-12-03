import os
import subprocess
import sys
import xmlrpc
import threading
import traceback
from xmlrpc.server import SimpleXMLRPCServer, SimpleXMLRPCRequestHandler
from abc import ABCMeta, abstractmethod
from enum import Enum

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QApplication,
    QWidget,
    QComboBox,
    QLineEdit,
    QCheckBox,
    QSlider,
    QHBoxLayout,
    QRadioButton,
)
from .qrangeslider import QRangeSlider
from ._config import python3_executable, torch_home

base_dir = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
models_dir = os.path.join(base_dir, 'models')

import logging

log = logging.getLogger("plugin_base")

class ParamWidget(object):
    def __init__(self, param):
        self._param = param

class ParamOption(ParamWidget, QComboBox):
    def __init__(self, param):
        ParamWidget.__init__(self, param)
        QComboBox.__init__(self)
        for option in self._param[4]:
            if type(option) is tuple:
                self.addItem(option[0], option[1])
            else:
                self.addItem(option, option)
        self.setCurrentIndex(param[3])
        self.currentIndexChanged.connect(self._update)

    def _update(self):
        self._param[3] = self.currentIndex()

class ParamInt(ParamWidget, QLineEdit):
    def __init__(self, param):
        ParamWidget.__init__(self, param)
        QLineEdit.__init__(self)
        from PyQt5.QtGui import QIntValidator
        self.setValidator(QIntValidator(0, 999))
        self.setText(str(self._param[3]))
        self.editingFinished.connect(self._update)

    def _update(self):
        self._param[3] = int(self.text())

class ParamFloat(ParamWidget, QLineEdit):
    def __init__(self, param):
        ParamWidget.__init__(self, param)
        QLineEdit.__init__(self)
        from PyQt5.QtGui import QDoubleValidator
        self.setValidator(QDoubleValidator(0.0, 1.0, 2, notation=QDoubleValidator.StandardNotation))
        self.setText(str(self._param[3]))
        self.editingFinished.connect(self._update)

    def _update(self):
        self._param[3] = float(self.text())

class ParamString(ParamWidget, QLineEdit):
    def __init__(self, param):
        ParamWidget.__init__(self, param)
        QLineEdit.__init__(self)
        self.setText(str(self._param[3]))
        self.editingFinished.connect(self._update)

    def _update(self):
        self._param[3] = self.text()

class ParamBool(ParamWidget, QCheckBox):
    def __init__(self, param):
        ParamWidget.__init__(self, param)
        QCheckBox.__init__(self)
        self.setChecked(self._param[3])
        self.stateChanged.connect(self._update)

    def _update(self):
        self._param[3] = self.isChecked()

class ParamSlider(ParamWidget, QSlider):
    def __init__(self, param):
        ParamWidget.__init__(self, param)
        QSlider.__init__(self, Qt.Orientation.Horizontal)
        try:
            range = self._param[4]
        except:
            range = (0,255)
        self.setRange(range[0], range[1])
        self.setValue(self._param[3])
        self.valueChanged.connect(self._update)

    def _update(self, value):
        self._param[3] = value

class ParamRangeSlider(ParamWidget, QRangeSlider):
    def __init__(self, param):
        ParamWidget.__init__(self, param)
        QRangeSlider.__init__(self)
        try:
            range = self._param[4]
        except:
            range = (0,255)
        self.setMin(range[0])
        self.setMax(range[1])
        self.setStart(self._param[3][0])
        self.setEnd(self._param[3][1])
        self.startValueChanged.connect(self._updateStart)
        self.endValueChanged.connect(self._updateEnd)

    def _updateStart(self, value):
        self._param[3][0] = value

    def _updateEnd(self, value):
        self._param[3][1] = value

class ParamRadio(ParamWidget, QWidget):
    def __init__(self, param):
        ParamWidget.__init__(self, param)
        QWidget.__init__(self)
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        for i, item in enumerate(self._param[4]):
            r = QRadioButton(item)
            r.setChecked(i == self._param[3])
            r.toggled.connect(self._update)
            layout.addWidget(r)
        layout.addStretch()
        self.setLayout(layout)

    def _update(self):
        radio = self.sender()
        value = self._param[4].index(radio.text())
        if radio.isChecked():
            self._param[3] = value

class Type(Enum):
    OPTION = ParamOption
    INT = ParamInt
    FLOAT = ParamFloat
    STRING = ParamString
    BOOL = ParamBool
    SLIDER = ParamSlider
    RADIO = ParamRadio
    RANGE = ParamRangeSlider

class FilterBase(QWidget):
    __metaclass__ = ABCMeta

    def __init__(self, parent, title, name, info, params):
        super().__init__(parent)
        self.model_file = None
        self.title = title
        self.name = name
        self.info = info
        self._params = params
        self._bounds = None
        self._force_cpu = False
        self._model_proxy = None
        self._message = None
        self.initUI()

    @abstractmethod
    def run(self, img, bounds):
        pass

    def initUI(self):
        from PyQt5.QtWidgets import QVBoxLayout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        layout.addWidget(self._paramsWidget())

    def _paramsWidget(self):

        from PyQt5.QtWidgets import QSizePolicy, QSpacerItem, QFrame, QScrollArea, QVBoxLayout, QFormLayout, QComboBox, QLineEdit, QCheckBox

        frame = QFrame(self)
        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        frame.setLayout(layout)

        # scrollarea
        scrollarea = QScrollArea()
        #scrollarea.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scrollarea.setWidgetResizable(True)
        layout.addWidget(scrollarea)

        # container
        container = QWidget()
        scrollarea.setWidget(container)
        container_layout = QVBoxLayout(container)
        container_layout.setContentsMargins(0, 0, 0, 0)
        layout = QFormLayout()
        container_layout.addLayout(layout)
        container_layout.addItem(QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum))

        for i, param in enumerate(self._params):
            widget = param[0].value(param)
            layout.addRow(param[2], widget)

        return frame

    @property
    def params(self):
        return {i[1]: i[3] for i in self._params}

    @property
    def app(self):
        from krita import Krita
        app = Krita.instance()
        return app

    @property
    def activeDocument(self):
        app = self.app
        doc = app.activeDocument()
        return doc

    @property
    def activeLayer(self):
        doc = self.activeDocument
        if doc:
            return doc.activeNode()
        else:
            return None

    def imgarray_to_qimage(self, x, mask=False):
        from krita import QImage
        if mask:
            x = QImage(x.buffer, x.shape[1], x.shape[0], QImage.Format_Grayscale8)
        else:
            x = QImage(x.buffer, x.shape[1], x.shape[0], QImage.Format_RGBA8888).rgbSwapped()
        return x

    def qimage_to_imgarray(self, x):
        rect = x.rect()
        ptr = x.constBits()
        ptr.setsize(x.byteCount())
        x = ImgArray(bytearray(ptr), (rect.height(), rect.width(), 4))
        return x

    def create_layer(self, result, name=None, doc=None, mask=False, resizeCanvas=False, reposition=False):
        name = name or self.activeLayer.name() + ' ' + self.name

        if doc is None:
            doc = self.activeDocument

        if mask:
            self.app.action('add_new_transparency_mask').trigger()
            layer = self.activeLayer
            layer.setName(name)
        else:
            layer = doc.createNode(name, "paintlayer")
            doc.rootNode().addChildNode(layer, None)

        img = self.imgarray_to_qimage(result, mask=mask)
        ptr = img.constBits() 
        ptr.setsize(img.byteCount())
        layer.setPixelData(bytearray(ptr), 0, 0, result.shape[1], result.shape[0])

        if resizeCanvas:
            h, w, _ = result.shape
            w = max(w, doc.width())
            h = max(h, doc.height())
            doc.setWidth(w)
            doc.setHeight(h)
        if reposition and self._bounds:
            layer.move(self._bounds.x(), self._bounds.y())

        if mask:
            doc.setActiveNode(layer.parentNode())
        else:
            doc.setActiveNode(layer)
        doc.refreshProjection()

        return layer

    def create_image(self, result, name=None):
        layer_name = self.activeLayer.name()
        name = name or layer_name + ' ' + self.name
        from krita import Krita
        app = Krita.instance()
        h, w, _ = result.shape
        doc = app.createDocument(w, h, name, "RGBA", "U8", "", 300)
        #layer = self.create_layer(result, name=layer_name, doc=doc)
        app.activeWindow().addView(doc)
        return doc

    def message(self, str=""):
        if self._message:
            self._message(str)

    def enabled(self):
        # A/RGBA/XYZA/LABA/CMYKA/GRAYA/YCbCrA
        layer = self.activeLayer
        if layer:
            color_model = layer.colorModel()
            return (color_model == "RGBA")
        return False

    def run_outer(self, message_cb=None):
        from krita import QImage
        self._message = message_cb
        layer = self.activeLayer
        bounds = layer.bounds()
        self._bounds = bounds
        data = layer.projectionPixelData(bounds.x(), bounds.y(), bounds.width(), bounds.height())
        img = QImage(data, bounds.width(), bounds.height(), QImage.Format_RGBA8888).rgbSwapped()
        print("Running {}...".format(self.name))
        self.message("Running {}...".format(self.name))
        self.run(img, bounds)

    def predict(self, *args, **kwargs):
        assert self.model_file is not None
        self._model_proxy = ModelProxy(self, self.model_file)
        kwargs["force_cpu"] = self._force_cpu
        try:
            result = self._model_proxy(*args, **kwargs)
            self._model_proxy = None
            return result
        except Exception as e:
            message = [m for m in str(e).split("\n") if m.strip()][-1]
            self.message(message)
            raise

    def kill(self):
        if self._model_proxy:
            self._model_proxy.kill()


class ModelProxy(object):
    """
    When called, runs
        python3 models/<model_file>
    and waits for the subprocess to call get_args() and then return_result() or raise_error() over XML-RPC.
    Additionally, progress info can be reported via update_progress().
    """

    def __init__(self, model, model_file):
        self.python_executable = python3_executable
        self.model = model
        self.model_path = os.path.join(models_dir, model_file)
        self.killswitch = threading.Event()
        self.server = None
        self.args = None
        self.kwargs = None
        self.result = None

    @staticmethod
    def _encode(x):
        from krita import QImage
        if isinstance(x, QImage):
            rect = x.rect()
            ptr = x.constBits()
            ptr.setsize(x.byteCount())
            x = ImgArray(bytearray(ptr), (rect.height(), rect.width(), 4))
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

    def _rpc_update_progress(self, progress, message):
        if progress:
            message = "{} ({:.1f}%)".format(message, progress*100.0)
        self.model.message(message)

    def _rpc_heartbeat(self):
        QApplication.processEvents()

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
                    try:
                        self.proc.wait(1)
                    except subprocess.TimeoutExpired:
                        pass
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
        self.server.register_function(self._rpc_update_progress, 'update_progress')
        self.server.register_function(self._rpc_heartbeat, 'heartbeat')
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

        if self.result is None:
            if self.killswitch.is_set():
                self.model.message("Cancelled")
            else:
                if self.server.exception:
                    if isinstance(self.server.exception, str):
                        raise RuntimeError(self.server.exception)
                    type, value, traceback = self.server.exception
                    #raise type, value, traceback
                self.model.message("Model did not return a result!")

        if self.result and len(self.result) == 1:
            return self.result[0]
        return self.result


class ImgArray(object):
    """Minimal bytearray object for serialization in RPC."""

    def __init__(self, buffer, shape):
        self.buffer = buffer
        self.shape = shape

    def encode(self):
        data = xmlrpc.client.Binary(self.buffer)
        return "ImgArray", data, self.shape

    @staticmethod
    def decode(x):
        data, shape = x[1:]
        data = data.data
        return ImgArray(data, shape)
