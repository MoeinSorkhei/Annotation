from PIL import Image, ImageTk
from matplotlib import cm
import pydicom
import numpy as np
import os
from pathlib import Path

import globals
from .helper import log


def get_dicom_files_paths(imgs_dir):
    paths = []
    for base_path, _, filenames in os.walk(imgs_dir):
        for f in sorted(filenames):  # always read the files sorted by name
            img_abs_path = os.path.abspath(os.path.join(base_path, f))
            paths.append(img_abs_path)
    return paths


def read_dicom_and_resize(file, only_save_to=None):
    # ======== read dicom file
    dataset = pydicom.dcmread(file)
    # print(dataset)
    # input()

    pixels = dataset.pixel_array
    pixels = pixels / np.max(pixels)  # normalize to 0-1

    orientation = str(dataset.get('PatientOrientation', "(missing)"))
    if 'A' in orientation:  # anterior view, should be flipped
        pixels = np.flip(pixels, axis=1)
    log('', no_time=True)  # extra print in log file for more readability

    # apply color map, rescale to 0-255, convert to int
    image = Image.fromarray(np.uint8(cm.bone(pixels) * 255))

    # resize image
    resize_factor = globals.params['resize_factor']
    if resize_factor is not None:
        image = image.resize((pixels.shape[1] // resize_factor, pixels.shape[0] // resize_factor))

    if only_save_to:
        image.save(only_save_to)
        return

    photo = ImageTk.PhotoImage(image)
    return photo


def all_dicoms_to_png(path, save=False):
    dicoms_list = list((Path(path).rglob("*.dcm")))
    dicoms_list = [str(dicom_path) for dicom_path in dicoms_list]

    if save:
        for dicom in dicoms_list:
            read_dicom_and_resize(dicom, dicom.replace('.dcm', '.png'))
    return dicoms_list
