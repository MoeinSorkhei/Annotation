import argparse
import os

import gui
import logic
from logic import *


def read_args_and_adjust():
    parser = argparse.ArgumentParser(description='Annotation tool')
    # parser.add_argument('--imgs_dir', type=str)
    # parser.add_argument('--output_path', type=str)
    parser.add_argument('--session_name', type=str)
    parser.add_argument('--which_bin', type=str)
    parser.add_argument('--debug', action='store_true')

    arguments = parser.parse_args()
    # params = logic.read_params(os.path.join('..', 'params.json'))
    # return arguments, params

    if arguments.debug:
        globals.debug = True
        log('In [read_args_and_adjust]: globals.debug set to True.')

    return arguments


# def adjust_params(args, params):
#     # if args.imgs_dir is not None:
#     #     params['imgs_dir'] = args.imgs_dir
#     #
#     # if args.output_path is not None:
#     #     params['output_path'] = args.output_path  # not used at the moment
#
#     return params


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
    # log(f'In [manage_sessions]: output path created: "{output_path}"...')

    # session_name = 'phase_1'
    # which_bin = '1'
    session_name = args.session_name
    which_bin = args.which_bin
    mode = 'single' if 'phase_1' in session_name else 'side_by_side'

    log(f"\n\n\n\n{'*' * 150} \n{'*' * 150} \n{'*' * 150} \n{'*' * 150}", no_time=True)
    log(f'In [manage_sessions]: session_name: "{session_name}" - Mode: {mode}')

    if 'phase_1' in session_name:
        imgs = logic.get_dicom_files_paths(imgs_dir=globals.params['imgs_dir'])  # the dicom files
        return mode, session_name, imgs

    else:
        file_as_lst, sorted_as_lst = read_img_names_from_file(which_bin)
        not_already_sorted = [img for img in file_as_lst if img not in sorted_as_lst]

        log(f'In [manage_sessions]: read file_as_lst of len: {len(file_as_lst)} and sorted_as_lst '
            f'of len: {len(sorted_as_lst)} - extracted {len(not_already_sorted)} images that are not already sorted\n\n')
        return mode, session_name, not_already_sorted


def main():
    args = read_args_and_adjust()
    mode, session_name, imgs = manage_sessions(args)

    if len(imgs) == 0:
        log(f'In [main]: images are of len: 0 ==> Session is already complete. Terminating...')
        exit(0)

    if len(imgs) == 1:
        log(f'In [main]: images are of len: 1 ==> No sorting is needed. Terminating...')
        exit(0)

    gui.show_window_with_keyboard_input(mode, imgs, session_name, args.which_bin)  # which_bin is None for phase 1


if __name__ == '__main__':
    main()
