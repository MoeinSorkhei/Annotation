import argparse

from gui import *
from logic import *
from logic import data_prep


def read_args_and_adjust():
    parser = argparse.ArgumentParser(description='Annotation tool')
    parser.add_argument('--annotator', type=str)
    parser.add_argument('--session_name', type=str)
    parser.add_argument('--data_mode', type=str)
    parser.add_argument('--n_bins', type=int)
    parser.add_argument('--resize_factor', type=int)
    parser.add_argument('--max_imgs_per_session', type=int)
    parser.add_argument('--email_interval', type=int)
    parser.add_argument('--ui_verbosity', type=int)   # set be set to 2 for moderate verbosity

    parser.add_argument('--debug', action='store_true')
    parser.add_argument('--email_results', action='store_true')  # used only for emailing results directly
    parser.add_argument('--no_email', action='store_true')

    # data preparation args
    parser.add_argument('--create_img_registry', action='store_true')
    parser.add_argument('--rename_test_imgs', action='store_true')
    parser.add_argument('--convert_test_imgs_to_png', action='store_true')
    parser.add_argument('--make_seed_list', action='store_true')
    parser.add_argument('--resize_data', action='store_true')
    parser.add_argument('--get_size_stats', action='store_true')

    arguments = parser.parse_args()

    if arguments.debug:
        globals.debug = True

    if arguments.resize_factor:
        globals.params['resize_factor'] = arguments.resize_factor

    if arguments.max_imgs_per_session:
        globals.params['max_imgs_per_session'] = arguments.max_imgs_per_session

    if arguments.email_interval:  # change default email interval
        globals.params['email_interval'] = arguments.email_interval

    if arguments.no_email:
        globals.params['email_interval'] = None

    return arguments


def show_window_with_keyboard_input(not_already_sorted, already_sorted,
                                    data_mode, ui_verbosity, train_bins=None):

    text = 'Which image is harder (even the slightest difference is important)? Press the corresponding button.'

    root = Tk()  # creates a blank window (or main window)
    title = Label(root, text=text, bg='light blue', font='-size 20')
    title.pack(fill=X)

    frame = Window(master=root,
                   cases=not_already_sorted,
                   already_sorted=already_sorted,
                   data_mode=data_mode,
                   ui_verbosity=ui_verbosity,
                   n_bins=train_bins)
    root.mainloop()  # run the main window continuously


def retrieve_not_already_sorted_files(data_mode):
    # create lists of images for test data
    if data_mode == 'test':
        img_lst = logic.get_dicom_files_paths(imgs_dir=globals.params['test_imgs_dir'])  # the dicom files
        already_sorted = read_sorted_imgs()
        n_bins = None

    # create lists of images for train data
    else:
        img_lst = logic.get_dicom_files_paths(imgs_dir=globals.params['train_imgs_dir'])
        n_bins, already_sorted = all_imgs_in_all_bins()  # images that are already entered to bins

    aborted_cases = read_aborted_cases()
    discarded_cases = read_discarded_cases()

    not_already_sorted = [img for img in img_lst if
                          (img not in already_sorted and img not in aborted_cases and img not in discarded_cases)]

    log(f'In [retrieve_not_already_sorted_files]: \n'
        f'read img_list of len: {len(img_lst)} \n'
        f'already_sorted (or entered into bins) images are of len: {len(already_sorted)} \n'
        f'aborted cases are of len: {len(aborted_cases)} \n'
        f'discarded cases are of len: {len(discarded_cases)} \n'
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

    ui_verbosity = 1  # default, least verbose
    if globals.debug:
        ui_verbosity = 4
    elif args.ui_verbosity is not None:
        ui_verbosity = args.ui_verbosity

    log(f"\n\n\n\n{'*' * 150} \n{'*' * 150} \n{'*' * 150} \n{'*' * 150}", no_time=True)
    log(f'In [manage_sessions]: session_name: "{session_name}" - data_mode: {data_mode} - annotator: {args.annotator}')

    assert session_name == 'sort' or session_name == 'split'
    if session_name == 'sort':
        not_already_sorted, already_sorted, n_bins = retrieve_not_already_sorted_files(data_mode)
        if len(not_already_sorted) == 0:
            log(f'In [main]: not_already_sorted images are of len: 0 ==> Session is already complete. Terminating...')
            exit(0)

        # reduce the number of images for a session to a ore-defined number
        max_imgs_per_session = globals.params['max_imgs_per_session']
        not_already_sorted = not_already_sorted[:max_imgs_per_session]
        log(f'In [manage_sessions]: not_already_sorted reduced to have len: {len(not_already_sorted)} in this session.')
        show_window_with_keyboard_input(not_already_sorted, already_sorted, data_mode, ui_verbosity, n_bins)

    else:
        split_sorted_list_to_bins(args.n_bins)


def main():
    args = read_args_and_adjust()

    if args.email_results:  # used only for emailing results
        log('In [main]: emailing results...')
        logic.email_results()

    elif args.create_img_registry:
        registry_file = globals.params['registry_file']
        data_prep.create_img_registry(img_folder=globals.params['test_imgs_dir'],
                                      output_file=registry_file)

    elif args.rename_test_imgs:
        data_prep.rename_test_imgs(globals.params['registry_file'],
                                   globals.params['test_imgs_dir'],
                                   globals.params['test_imgs_renamed_dir'])

    elif args.convert_test_imgs_to_png:
        data_prep.convert_test_imgs_to_png()

    elif args.make_seed_list:
        data_prep.make_seed_list()

    elif args.resize_data:
        print('Resizing data...')
        resize_factor = 4
        mean_width, mean_height = 3219, 5400  # taken from some 50 ddsm images
        resize_width, resize_height = mean_width // resize_factor, mean_height // resize_factor

        # for test data
        image_dir = globals.params['test_imgs_dir']
        save_dir = os.path.join(globals.params['data_path'], 'test_imgs_resized')
        data_prep.resize_data(image_dir, save_dir, resize_width, resize_height)
        print('\nResizing for test data: done\n')

        # for train data
        image_dir = globals.params['train_imgs_dir']
        save_dir = os.path.join(globals.params['data_path'], 'train_imgs_resized')
        data_prep.resize_data(image_dir, save_dir, resize_width, resize_height)
        print('Resizing for train data: done')

    elif args.get_size_stats:
        data_prep.get_size_stats(globals.params['test_imgs_dir'])
        data_prep.get_size_stats(globals.params['train_imgs_dir'])

    else:
        if args.annotator is None:
            print('Please provide annotator name using the --annotator argument')
            exit(1)  # unsuccessful exit

        manage_sessions_and_run(args)


if __name__ == '__main__':
    main()


# SCRIPTS:
# =========  On my mac:
# python3 main.py --annotator Moein --session_name sort --data_mode test --resize_factor 15 --debug
# python3 main.py --annotator Moein --session_name sort --data_mode train --resize_factor 15 --debug
# python3 main.py --annotator Moein --session_name split --n_bins 2 --debug

# python3 main.py --session sort --data_mode test --debug --resize_factor 10 --max_imgs_per_session 4 --email_interval 1


# data preparation:
# python3 main.py --make_seed_list
# python3 main.py --resize_data

# actual run
# use --email_interval option
# use --max_imgs_per_session option
# use --resize_factor option
