import numpy as np
import os

import globals
from .helper import *


# ========== functions related to operations on the bins
def compute_file_paths_for_bin(rate=None, which_bin=None):  # THIS FUNCTION WILL NO LONGER BE NEEDED
    output_path = globals.params['output_path']

    # for phase 1 -- only need bin_1.txt
    if rate is not None:  # session name is ignored
        filename = os.path.join(output_path, f'bin_{rate}.txt')  # e.g., output/bin_1.txt
        sorted_filename = os.path.join(output_path, f'bin_{rate}_sorted.txt')
        return filename, sorted_filename

    # for phase 2
    if which_bin is not None:
        filename = os.path.join(output_path, f'bin_{which_bin}.txt')  # e.g., output/bin_1.txt
        sorted_filename = os.path.join(output_path, f'bin_{which_bin}_sorted.txt')  # output/bin_1_sorted.txt
        return filename, sorted_filename


def get_bin_path(which_bin):
    output_path = globals.params['output_path']
    bin_file = os.path.join(output_path, f'bin_{which_bin + 1}.txt')
    return bin_file


def bin_paths():
    output_path = globals.params['output_path']
    paths = []
    for base_path, _, filenames in os.walk(output_path):
        for f in sorted(filenames):
            if f.startswith('bin_'):
                paths.append(os.path.abspath(os.path.join(base_path, f)))
    return paths


def read_imgs_from_bin(which_bin):
    bin_file = get_bin_path(which_bin)
    with open(bin_file) as f:
        imgs_in_bin = f.read().splitlines()
    return imgs_in_bin


def read_sorted_imgs():
    sorted_filename = globals.params['sorted']
    sorted_lst = []  # empty list if the sorted file does not exists (ie the first time we want to sort)

    if os.path.isfile(sorted_filename):
        with open(sorted_filename) as f:
            sorted_lst = f.read().splitlines()
    return sorted_lst


def split_sorted_list_to_bins(n_bins):
    sorted_list = read_sorted_imgs()
    split_arr = np.array_split(sorted_list, n_bins)
    log(f'In [split_sorted_list_to_bins]: split the sorted list into {n_bins} bins: done')

    for i in range(len(split_arr)):
        bin_num = i + 1
        filename = os.path.join(globals.params['output_path'], f'bin_{bin_num}.txt')
        write_list_to_file(split_arr[i], filename)

    log(f'In [split_sorted_list_to_bins]: writing all the bins to files: done \n')


def insert_into_bin_and_save(which_bin, pos, img):
    bin_images = read_imgs_from_bin(which_bin)
    insertion_index = len(bin_images) if pos == 'last' else len(bin_images) - 1
    bin_images.insert(insertion_index, img)
    log(f'In [insert_into_bin_and_save]: inserting image to the "{pos}" of the bin {which_bin + 1}: done')
    save_bin(which_bin, bin_images)


def del_from_bin_and_save(which_bin, pos):
    bin_imgs = read_imgs_from_bin(which_bin)
    del_index = len(bin_imgs) - 1 if pos == 'last' else len(bin_imgs) - 2
    del bin_imgs[del_index]
    log(f'In [del_from_bin_and_save]: deleting image from the "{pos}" of the bin {which_bin + 1}: done')
    save_bin(which_bin, bin_imgs)


def save_bin(which_bin, bin_imgs):
    filename = get_bin_path(which_bin)
    with open(filename, 'w') as f:
        for img in bin_imgs:
            f.write(f'{img}\n')
    log(f'In [save_bin]: saving bin to "{filename}": done \n')


def last_img_in_bin(which_bin):
    return read_imgs_from_bin(which_bin)[-1]


def all_imgs_in_all_bins():
    paths = bin_paths()
    all_bins_imgs = []

    for path in paths:
        with open(path) as f:
            all_bins_imgs.extend(f.read().splitlines())
    return len(paths), all_bins_imgs
