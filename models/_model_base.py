import os
import traceback
from abc import ABC, abstractmethod
from xmlrpc.client import ServerProxy, Binary

import time
import threading
import numpy as np
import torch
from PIL import Image

import sys
import logging

#logging.basicConfig(level=logging.DEBUG)
log = logging.getLogger("model_base")


class ModelBase(ABC):
    def __init__(self):
        self.hub_repo = None
        self.device = None
        self._rpc = None
        self._model = None
        self._exception = None
        self._mutex = threading.Lock()

    @property
    def model(self):
        if self._model is None:
            with capture_tqdm(self.update_progress, "Downloading model"):
                self._model = self.load_model()
        return self._model

    @abstractmethod
    def load_model(self):
        raise NotImplementedError

    @abstractmethod
    def predict(self, *args, **kwargs):
        raise NotImplementedError

    def update_progress(self, percent, message):
        try:
            self._rpc.update_progress(percent, message)
        except:
            pass

    def heartbeat(self):
        self._mutex.acquire()
        try:
            if self._exception is None:
                self._rpc.heartbeat()
        finally:
            self._mutex.release()

    @staticmethod
    def _decode(x):
        if isinstance(x, list) and len(x) == 3 and x[0] == "ImgArray":
            data, shape = x[1:]
            data = data.data
            x = np.frombuffer(data, dtype=np.uint8).reshape(shape)
        return x

    @staticmethod
    def _encode(x):
        if isinstance(x, np.ndarray):
            x = ("ImgArray", Binary(x.astype(np.uint8).tobytes()), x.shape)
        return x

    def _decode_rpc_args(self, args, kwargs):
        args = [self._decode(arg) for arg in args]
        kwargs = {k: self._decode(v) for k, v in kwargs.items()}
        return args, kwargs

    def _encode_rpc_result(self, result):
        if not isinstance(result, (list, tuple)):
            result = [result]
        return [self._encode(x) for x in result]

    def start_heartbeat(self):
        def send_heartbeat():
            while True:
                self.heartbeat()
                time.sleep(1)
        threading.Thread(target=send_heartbeat, daemon=True).start()

    def process_rpc(self, rpc_url):
        log.debug("Processing using communication over {}".format(rpc_url))
        self._exception = None
        self._rpc = ServerProxy(rpc_url, allow_none=True)
        try:
            args, kwargs = self._decode_rpc_args(*self._rpc.get_args())
            self.start_heartbeat()
            if not kwargs.get("force_cpu", None) is None:
                force_cpu = kwargs.get("force_cpu")
                kwargs.pop("force_cpu")
            else:
                force_cpu = os.environ.get("TORCH_FORCE_CPU", 0)
            if force_cpu:
                self.device = torch.device("cpu")
            else:
                if torch.cuda.is_available():
                    self.device = torch.device("cuda")
                elif torch.backends.mps.is_available():
                    self.device = torch.device("mps")
                else:
                    self.device = torch.device("cpu")
            log.info("Device: {}".format(self.device))
            log.debug("Input: {}".format(args[0].shape))
            result = self.predict(*args, **kwargs)
            log.debug("Result: {}".format(result.shape))
        except Exception as e:
            log.debug(e)
            self._mutex.acquire()
            self._exception = e
            self._mutex.release()
            self._rpc.raise_exception(traceback.format_exc())
            return

        result = self._encode_rpc_result(result)
        self._rpc.return_result(result)


class capture_tqdm:
    def __init__(self, progress_fn, default_desc=None):
        self.progress_fn = progress_fn
        self.default_desc = default_desc

    def __enter__(self):
        from tqdm import tqdm
        self.tqdm_display = tqdm.display

        def custom_tqdm_display(tqdm_self, *args, **kwargs):
            tqdm_info = tqdm_self.format_dict.copy()
            tqdm_info["prefix"] = tqdm_info["prefix"] or self.default_desc
            tqdm_info["bar_format"] = "{desc}: " if tqdm_info["prefix"] else ""
            # Removed {percentage:3.0f}% from bar_format
            tqdm_info["bar_format"] += "{n_fmt}/{total_fmt} [{elapsed}<{remaining}, {rate_fmt}{postfix}]"
            message = tqdm_self.format_meter(**tqdm_info)
            percent = None
            if tqdm_info["total"]:
                percent = tqdm_info["n"] / float(tqdm_info["total"])
            self.progress_fn(percent, message)
            self.tqdm_display(tqdm_self, *args, **kwargs)

        tqdm.display = custom_tqdm_display
        return self

    def __exit__(self, exit_type, exit_value, exit_traceback):
        from tqdm import tqdm
        tqdm.display = self.tqdm_display

    def __call__(self, func):
        def decorator(*args, **kwargs):
            with self:
                return func(*args, **kwargs)

        return decorator


def split_alpha(array):
    h, w, d = array.shape
    if d == 1:
        return array, None
    if d == 2:
        return array[:, :, 0:1], array[:, :, 1:2]
    if d == 3:
        return array, None
    if d == 4:
        return array[:, :, 0:3], array[:, :, 3:4]
    raise ValueError("Image has too many channels ({})".format(d))


def merge_alpha(image, alpha):
    h, w, d = image.shape
    if d not in (1, 3):
        raise ValueError("Incorrect number of channels ({})".format(d))
    if alpha is None:
        return image
    return np.concatenate([image, alpha], axis=2)


def combine_alphas(alphas):
    combined_alpha = None
    for alpha in alphas:
        if alpha is not None:
            if combined_alpha is None:
                combined_alpha = alpha
            else:
                combined_alpha = combined_alpha * (alpha / 255.)
    if combined_alpha is not None:
        combined_alpha = combined_alpha.astype(np.uint8)
    return combined_alpha


def handle_alpha(func):
    def decorator(*args, **kwargs):
        alphas = []
        args = list(args)
        for i, arg in enumerate(args):
            if isinstance(arg, np.ndarray):
                img, alpha = split_alpha(arg)
                args[i] = img
                alphas.append(alpha)
        for key, arg in list(kwargs.items()):
            if isinstance(arg, np.ndarray):
                img, alpha = split_alpha(arg)
                kwargs[key] = img
                alphas.append(alpha)

        result = func(*args, **kwargs)
        alpha = combine_alphas(alphas)

        # for super-res
        if alpha is not None and result.shape[:2] != alpha.shape[:2]:
            h, w, d = result.shape
            alpha = np.array(Image.fromarray(alpha[..., 0]).resize((w, h), Image.BILINEAR))[..., None]

        result = merge_alpha(result, alpha)
        return result

    return decorator
