"""
This module provides the LaMa (Large Mask Inpainting) model for image inpainting.
"""
import os
import sys
import hashlib
import logging
from typing import Union
from urllib.parse import urlparse

import numpy as np
import torch
from torch.hub import download_url_to_file, get_dir

LAMA_MODEL_URL = os.environ.get(
    "LAMA_MODEL_URL",
    "https://github.com/Sanster/models/releases/download/add_big_lama/big-lama.pt",
)
LAMA_MODEL_MD5 = os.environ.get("LAMA_MODEL_MD5", "e3aa4aaa15225a33ec84f9f4bc47e500")


def md5sum(filename: str) -> str:
    """Calculates the MD5 checksum of a file."""
    md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(128 * md5.block_size), b""):
            md5.update(chunk)
    return md5.hexdigest()


def handle_error(model_path: str, model_md5: str, error: str) -> None:
    """Handles errors during model loading."""
    _md5 = md5sum(model_path)
    if _md5 != model_md5:
        try:
            os.remove(model_path)
            logging.error(
                "Model md5: %s, expected md5: %s, wrong model deleted.",
                _md5,
                model_md5,
            )
        except OSError:
            logging.error(
                "Model md5: %s, expected md5: %s, please delete %s and restart.",
                _md5,
                model_md5,
                model_path,
            )
    else:
        logging.error(
            "Failed to load model %s. Error: %s",
            model_path,
            error,
        )
    sys.exit(-1)


def get_cache_path_by_url(url: str) -> str:
    """Gets the cache path for a given URL."""
    parts = urlparse(url)
    hub_dir = get_dir()
    model_dir = os.path.join(hub_dir, "checkpoints")
    if not os.path.isdir(model_dir):
        os.makedirs(model_dir)
    filename = os.path.basename(parts.path)
    cached_file = os.path.join(model_dir, filename)
    return cached_file


def download_model(url: str, model_md5: str = None) -> str:
    """Downloads a model from a URL."""
    cached_file = get_cache_path_by_url(url)
    if not os.path.exists(cached_file):
        sys.stderr.write(f'Downloading: "{url}" to {cached_file}\n')
        hash_prefix = None
        download_url_to_file(url, cached_file, hash_prefix, progress=True)
        if model_md5:
            _md5 = md5sum(cached_file)
            if model_md5 == _md5:
                logging.info("Download model success, md5: %s", _md5)
            else:
                try:
                    os.remove(cached_file)
                    logging.error(
                        "Model md5: %s, expected md5: %s, wrong model deleted.",
                        _md5,
                        model_md5,
                    )
                except OSError:
                    logging.error(
                        "Model md5: %s, expected md5: %s, please delete %s and restart.",
                        _md5,
                        model_md5,
                        cached_file,
                    )
                sys.exit(-1)
    return cached_file


def load_jit_model(
    url_or_path: str,
    device: Union[torch.device, str],
    model_md5: str,
) -> torch.jit._script.RecursiveScriptModule:
    """Loads a JIT model from a URL or path."""
    if os.path.exists(url_or_path):
        model_path = url_or_path
    else:
        model_path = download_model(url_or_path, model_md5)

    logging.info("Loading model from: %s", model_path)
    try:
        model = torch.jit.load(model_path, map_location="cpu").to(device)
    except Exception as e:
        handle_error(model_path, model_md5, str(e))
    model.eval()
    return model


def norm_img(np_img: np.ndarray) -> np.ndarray:
    """Normalizes an image."""
    if len(np_img.shape) == 2:
        np_img = np_img[:, :, np.newaxis]
    np_img = np.transpose(np_img, (2, 0, 1))
    np_img = np_img.astype("float32") / 255
    return np_img


def ceil_modulo(x_val: int, mod: int) -> int:
    """Calculates the ceiling of a number modulo another number."""
    if x_val % mod == 0:
        return x_val
    return (x_val // mod + 1) * mod


def pad_img_to_modulo(img: np.ndarray, mod: int) -> np.ndarray:
    """Pads an image to a multiple of a given number."""
    if len(img.shape) == 2:
        img = img[:, :, np.newaxis]
    height, width = img.shape[:2]
    out_height = ceil_modulo(height, mod)
    out_width = ceil_modulo(width, mod)
    return np.pad(
        img,
        ((0, out_height - height), (0, out_width - width), (0, 0)),
        mode="symmetric",
    )


class LaMa:
    """LaMa inpainting model."""

    name = "lama"
    pad_mod = 8

    def __init__(self, device: Union[torch.device, str]) -> None:
        self.device = device
        self.model = load_jit_model(LAMA_MODEL_URL, device, LAMA_MODEL_MD5).eval()

    @staticmethod
    def is_downloaded() -> bool:
        """Checks if the model is downloaded."""
        return os.path.exists(get_cache_path_by_url(LAMA_MODEL_URL))

    def forward(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        Input image and output image have same size
        image: [H, W, C] RGB
        mask: [H, W]
        return: RGB IMAGE
        """
        dtype = image.dtype
        image = norm_img(image)
        mask = norm_img(mask if np.max(mask) > 1.0 else mask * 2)

        mask = (mask > 0) * 1
        image = torch.from_numpy(image).unsqueeze(0).to(self.device)
        mask = torch.from_numpy(mask).unsqueeze(0).to(self.device)

        inpainted_image = self.model(image, mask)

        cur_res = inpainted_image[0].permute(1, 2, 0).detach().cpu().numpy()
        cur_res = np.clip(cur_res * 255, 0, 255)
        return cur_res.astype(dtype)

    @torch.no_grad()
    def __call__(self, image: np.ndarray, mask: np.ndarray) -> np.ndarray:
        """
        images: [H, W, C] RGB, not normalized
        masks: [H, W]
        return: RGB IMAGE
        """
        dtype = image.dtype
        origin_height, origin_width = image.shape[:2]
        pad_image = pad_img_to_modulo(image, mod=self.pad_mod)
        pad_mask = pad_img_to_modulo(mask, mod=self.pad_mod)

        result = self.forward(pad_image, pad_mask)
        result = result[0:origin_height, 0:origin_width, :]

        mask = mask[:, :, np.newaxis]
        mask = mask / 255 if np.max(mask) > 1.0 else mask
        result = result * mask + image * (1 - mask)
        return result.astype(dtype)
