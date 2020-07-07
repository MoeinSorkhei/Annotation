import argparse

from gui import *
from logic import *


def read_args_and_adjust():
    parser = argparse.ArgumentParser(description='Annotation tool')
    parser.add_argument('--session_name', type=str)
    parser.add_argument('--data_mode', type=str)
    parser.add_argument('--n_bins', type=int)
    parser.add_argument('--resize_factor', type=int)

    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--email_results', action='store_true')

    arguments = parser.parse_args()

    if arguments.debug:
        globals.debug = True

    if arguments.resize_factor:
        globals.params['resize_factor'] = arguments.resize_factor

    return arguments


def show_window_with_keyboard_input(mode, not_already_sorted, already_sorted, already_comparisons,
                                    data_mode, search_type, train_bins=None):
    if mode == 'single':
        text = 'How hard the image is? 1:  Easy, 2: Medium, 3: Hard'

    else:  # only 'binary_insert'
        text = 'Which image is harder? 1: Left - 2: Right - 9: No difference ' \
               '(Note: Even the slightest difference is important).'

    root = Tk()  # creates a blank window (or main window)
    title = Label(root, text=text, bg='light blue', font='-size 20')
    title.pack(fill=X)

    frame = Window(master=root,
                   cases=not_already_sorted,
                   already_sorted=already_sorted,
                   already_comparisons=already_comparisons,
                   show_mode=mode,
                   data_mode=data_mode,
                   search_type=search_type,
                   train_bins=train_bins)
    root.mainloop()  # run the main window continuously


def retrieve_not_already_sorted_files(data_mode):
    # create lists of images for test data
    if data_mode == 'test':
        img_lst = logic.get_dicom_files_paths(imgs_dir=globals.params['main_imgs_dir'])  # the dicom files
        already_sorted = read_sorted_imgs()
        n_bins = None

    # create lists of images for train data
    else:
        img_lst = logic.get_dicom_files_paths(imgs_dir=globals.params['other_imgs_dir'])
        n_bins, already_sorted = all_imgs_in_all_bins()  # images that are already entered to bins

    aborted_cases = read_aborted_cases()
    not_already_sorted = [img for img in img_lst if (img not in already_sorted and img not in aborted_cases)]

    log(f'In [retrieve_not_already_sorted_files]: \n'
        f'read img_list of len: {len(img_lst)} \n'
        f'already_sorted (or entered into bins) images are of len: {len(already_sorted)} \n'
        f'aborted cases are of len: {len(aborted_cases)} \n'
        f'there are {len(not_already_sorted)} images that are not already sorted and not aborted \n')

    return not_already_sorted, already_sorted, n_bins


def manage_sessions_and_run(args):
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
    data_mode = args.data_mode
    mode = 'side_by_side'
    search_type = globals.params['search_type']

    log(f"\n\n\n\n{'*' * 150} \n{'*' * 150} \n{'*' * 150} \n{'*' * 150}", no_time=True)
    log(f'In [manage_sessions]: session_name: "{session_name}" - data_mode: {data_mode}')

    if 'sort' in session_name:
        # create lists of images for test data
        # if data_mode == 'test':
        #     img_lst = logic.get_dicom_files_paths(imgs_dir=globals.params['main_imgs_dir'])  # the dicom files
        #     already_sorted = read_sorted_imgs()
        #     n_bins = None
        #
        # # create lists of images for train data
        # else:
        #     img_lst = logic.get_dicom_files_paths(imgs_dir=globals.params['other_imgs_dir'])
        #     n_bins, already_sorted = all_imgs_in_all_bins()  # images that are already entered to bins
        #
        # not_already_sorted = [img for img in img_lst if img not in already_sorted]
        # log(f'In [manage_sessions]: read img_list of len: {len(img_lst)}, already_sorted (or entered into bins) images are '
        #     f'of len: {len(already_sorted)} - there are {len(not_already_sorted)} images that are not already sorted')

        # return if all the images are already sorted

        not_already_sorted, already_sorted, n_bins = retrieve_not_already_sorted_files(data_mode)
        if len(not_already_sorted) == 0:
            log(f'In [main]: not_already_sorted images are of len: 0 ==> Session is already complete. Terminating...')
            exit(0)

        # reduce the number of images for a session to a ore-defined number
        max_imgs_per_session = globals.params['max_imgs_per_session']
        not_already_sorted = not_already_sorted[:max_imgs_per_session]
        log(f'In [manage_sessions]: not_already_sorted reduced to have len: {len(not_already_sorted)} in this session.')

        already_comparisons = read_comparison_lists()
        log(f'In [manage_sessions]: already_comparisons loaded/created of {len(already_comparisons)} keys in it. \n\n')

        show_window_with_keyboard_input(mode, not_already_sorted, already_sorted, already_comparisons,
                                        data_mode, search_type, n_bins)

    elif session_name == 'split':
        split_sorted_list_to_bins(args.n_bins)

    else:
        raise NotImplementedError


def main():
    args = read_args_and_adjust()

    if args.email_results:  # used only for emailing results
        log('In [main]: emailing results...')
        logic.email_results()

    else:
        manage_sessions_and_run(args)


if __name__ == '__main__':
    main()


# SCRIPTS:
# =========  On my mac:
# /Users/user/.conda/envs/ADL/bin/python main.py --session sort --data_mode test --debug
# /Users/user/.conda/envs/ADL/bin/python main.py --session sort --data_mode test --debug
# /Users/user/.conda/envs/ADL/bin/python main.py --session sort --data_mode train --debug
# /Users/user/.conda/envs/ADL/bin/python main.py --session_name split --n_bins 2 --debug

# /Users/user/.conda/envs/ADL/bin/python test.py

