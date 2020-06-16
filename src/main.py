import argparse
import os

import gui
import logic
from logic import *


def read_args_and_adjust():
    parser = argparse.ArgumentParser(description='Annotation tool')
    parser.add_argument('--session_name', type=str)
    parser.add_argument('--n_bins', type=int)
    parser.add_argument('--debug', action='store_true')

    arguments = parser.parse_args()

    if arguments.debug:
        globals.debug = True

    return arguments


def manage_sessions(args):
    """
    :param args:
    :return:

    Notes on output files:
        - Comparisons.txt and comparisons.json are updated only once the decision is confirmed.
    """
    # creating output path if not exists
    output_path = globals.params['output_path']
    make_dir_if_not_exists(output_path)

    session_name = args.session_name
    mode = 'side_by_side'

    log(f"\n\n\n\n{'*' * 150} \n{'*' * 150} \n{'*' * 150} \n{'*' * 150}", no_time=True)
    log(f'In [manage_sessions]: session_name: "{session_name}" - Mode: {mode}')

    if 'sort_test' in session_name:
        img_lst = logic.get_dicom_files_paths(imgs_dir=globals.params['imgs_dir'])  # the dicom files
        sorted_lst = read_sorted_imgs()
        not_already_sorted = [img for img in img_lst if img not in sorted_lst]

        log(f'In [manage_sessions]: read file_as_lst of len: {len(img_lst)} and sorted_as_lst '
            f'of len: {len(sorted_lst)} - extracted {len(not_already_sorted)} images that are not already sorted\n\n')

        if len(not_already_sorted) == 0:
            log(f'In [main]: not_already_sorted images are of len: 0 ==> Session is already complete. Terminating...')
            exit(0)

        if len(not_already_sorted) == 1:
            log(f'In [main]: not_already_sorted images are of len: 1 ==> No sorting is needed. Terminating...')
            exit(0)

        gui.show_window_with_keyboard_input(mode, not_already_sorted, session_name)  # which_bin is None for phase 1

    elif session_name == 'split':
        split_sorted_list_to_bins(args.n_bins)

    else:
        raise NotImplementedError


def main():
    args = read_args_and_adjust()
    manage_sessions(args)


if __name__ == '__main__':
    main()
