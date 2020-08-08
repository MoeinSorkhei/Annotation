from PIL import Image, ImageTk
from matplotlib import cm
import pydicom
import numpy as np
import os
from pathlib import Path
import glob

import globals
from .helper import log
from . import helper


def get_dicom_files_paths(imgs_dir):
    paths = []
    for base_path, _, filenames in os.walk(imgs_dir):
        for f in sorted(filenames):  # always read the files sorted by name
            img_abs_path = os.path.abspath(os.path.join(base_path, f))
            paths.append(img_abs_path)
    return paths


def dicom_as_dataset(dicom_file):
    return pydicom.dcmread(dicom_file)


def resize_pixel_array(dicom_file, resize_width, resize_height, save_dir):
    dataset = pydicom.dcmread(dicom_file)
    pixel_array = dataset.pixel_array
    resized_pixel_array = np.array(Image.fromarray(pixel_array).resize(size=(resize_width, resize_height)))

    dataset.PixelData = resized_pixel_array.tobytes()  # copy the data back to the original data set
    dataset.Rows, dataset.Columns = resized_pixel_array.shape  # update the information about the shape of the data array

    save_path = os.path.join(save_dir, helper.pure_name(dicom_file))  # in save_dir with the same filename
    helper.make_dir_if_not_exists(save_dir)
    dataset.save_as(save_path)
    log(f'In [resize_pixel_array]: saved resized file to: "{save_path}"')


def read_dicom_and_resize(file, save_to=None):
    dataset = pydicom.dcmread(file)
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

    if save_to:
        image.save(save_to)
    return image


def image_list_to_png(image_list, save_path):
    for filepath in image_list:  # image_list should have absolute file paths
        png_filename = helper.pure_name(filepath).replace('.dcm', '.png')
        read_dicom_and_resize(filepath, save_to=os.path.join(save_path, png_filename))


def convert_imgs_to_png(source_dir, dest_dir):
    all_dicoms = sorted(glob.glob(f'{source_dir}/**/*.dcm', recursive=True))  # it assumes '/' path separator

    for dicom_file in all_dicoms:
        png_file = os.path.join(dest_dir, dicom_file.replace(f'{source_dir}/', '').replace('.dcm', '.png'))  # relative name
        print(f'Doing for dicom: "{dicom_file}"')

        sub_folders = os.path.split(png_file)[0]
        helper.make_dir_if_not_exists(sub_folders, verbose=False)  # create all the sub-folders needed
        read_dicom_and_resize(dicom_file, save_to=png_file)

    print('In [convert_imgs_to_png]: all done')
