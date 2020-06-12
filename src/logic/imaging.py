from PIL import Image, ImageTk
from matplotlib import cm
import pydicom
import numpy as np

import globals
from .helper import log


def read_dicom_and_resize(file):
    # ======== read dicom file
    dataset = pydicom.dcmread(file)
    pixels = dataset.pixel_array
    pixels = pixels / np.max(pixels)  # normalize to 0-1

    orientation = str(dataset.get('PatientOrientation', "(missing)"))
    log(f'In [read_dicom_image]: orientation: "{orientation}"')
    if 'A' in orientation:  # anterior view, should be flipped
        log(f'In [read_dicom_image]: the view is Anterior. Image is flipped when shown.')
        pixels = np.flip(pixels, axis=1)
    log('', no_time=True)  # extra print in log file for more readability

    # apply color map, rescale to 0-255, convert to int
    image = Image.fromarray(np.uint8(cm.bone(pixels) * 255))

    resize_factor = globals.params['resize_factor']
    if resize_factor is not None:
        resized = image.resize((pixels.shape[1] // resize_factor, pixels.shape[0] // resize_factor))
        photo = ImageTk.PhotoImage(resized)
    else:  # no resize
        photo = ImageTk.PhotoImage(image)
    return photo
