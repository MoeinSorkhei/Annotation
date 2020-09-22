import argparse

from gui import *
from logic import *
from logic import data_prep


def read_args_and_adjust():
    parser = argparse.ArgumentParser(description='Annotation tool')
    parser.add_argument('--annotator', type=str)
    parser.add_argument('--new', action='store_true')
    parser.add_argument('--already', action='store_true')
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
    parser.add_argument('--convert_to_png', action='store_true')
    parser.add_argument('--image_list', type=str)
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


def show_window_with_keyboard_input(not_already_sorted, already_sorted, session_name,
                                    data_mode, annotator, ui_verbosity, train_bins=None):

    text = 'Which image is harder (even the slightest difference is important)? Press the corresponding button on the keyboard.'

    root = Tk()  # creates a blank window (or main window)
    title = Label(root, text=text, bg='light blue', font='-size 20')
    title.pack(fill=X)

    frame = Window(master=root,
                   cases=not_already_sorted,
                   already_sorted=already_sorted,
                   data_mode=data_mode,
                   session_name=session_name,
                   annotator=annotator,
                   ui_verbosity=ui_verbosity,
                   n_bins=train_bins)
    root.mainloop()  # run the main window continuously


# def retrieve_not_already_sorted_files(session_name, data_mode):
#     # img_lst = helper.read_file_to_list(globals.params['img_registry'])
#     # if session_name == 'sort':
#     #     if data_mode == 'test':
#     #         already_sorted = read_sorted_imgs()
#     #         n_bins = None
#     #         text = 'sorted list len'
#     #     else:
#     #         n_bins, already_sorted = all_imgs_in_all_bins()  # images that are already entered to bins
#     #         text = 'total images in the bins'
#     #     aborted_cases = read_aborted_cases()
#     #     discarded_cases = read_discarded_cases()
#     # else:
#     #     already_sorted, n_bins, text = read_file_to_list(globals.params['rating']), None, f'total {session_name} rated images'
#     #     aborted_cases = discarded_cases = []
#     #
#     # not_already_sorted = [img for img in img_lst if
#     #                       (img not in already_sorted and img not in aborted_cases and img not in discarded_cases)]
#     img_lst, not_already_sorted, already_sorted, aborted_cases, discarded_cases, n_bins, text = to_be_rated(session_name, data_mode)
#
#     log(f'In [retrieve_not_already_sorted_files]: \n'
#         f'read img_list of len: {len(img_lst)} \n'
#         f'{text}: {len(already_sorted)} \n'
#         f'aborted cases: {len(aborted_cases)} \n'
#         f'discarded cases: {len(discarded_cases)} \n'
#         f'images left to be rated: {len(not_already_sorted)} \n')
#
#     return not_already_sorted, already_sorted, n_bins


def manage_sessions_and_run(args):
    session_name = args.session_name
    data_mode = args.data_mode
    annotator = args.annotator

    ui_verbosity = 1  # default, least verbose
    if globals.debug:
        ui_verbosity = 4
    elif args.ui_verbosity is not None:
        ui_verbosity = args.ui_verbosity

    # make seed list for annotator if this is the first time
    if args.session_name == 'sort' and args.data_mode == 'test' and args.new:
        log('In [main]: Creating the seed list for the annotator...')
        data_prep.make_seed_list()

    # log indicating start of a session
    log(f"\n\n\n\n{'*' * 150} \n{'*' * 150} \n{'*' * 150} \n{'*' * 150}", no_time=True)
    log(f'Session started in {get_datetime()}')
    log(f'In [manage_sessions]: session_name: "{session_name}" - data_mode: {data_mode} - annotator: {annotator}')

    # adding current date and time to the ratings file, only for sort sessions
    if session_name == 'sort':
        with open(globals.params['ratings'], 'a') as rate_file:
            string = f'{"#" * 20} Ratings for session in {get_datetime()} - Data: {data_mode} - Annotator: {args.annotator}'
            rate_file.write(f'{string}\n')
            log('In [manage_sessions]: current session date time and the annotator written to the ratings file.\n')

    # not_already_sorted, already_sorted, n_bins = retrieve_not_already_sorted_files(session_name, data_mode)
    img_lst, not_already_sorted, already_sorted, aborted_cases, discarded_cases, n_bins, text = to_be_rated(session_name, data_mode)

    log(f'In [manage_sessions]: \n'
        f'read img_list of len: {len(img_lst)} \n'
        f'{text}: {len(already_sorted)} \n'
        f'aborted cases: {len(aborted_cases)} \n'
        f'discarded cases: {len(discarded_cases)} \n'
        f'images left to be rated: {len(not_already_sorted)} \n')

    if len(not_already_sorted) == 0:
        log(f'In [main]: not_already_sorted images are of len: 0 ==> Session is already complete. Terminating...')
        exit(0)

    # reduce the number of images for a session to a ore-defined number
    max_imgs_per_session = globals.params['max_imgs_per_session']
    not_already_sorted = not_already_sorted[:max_imgs_per_session]
    log(f'In [manage_sessions]: not_already_sorted reduced to have len: {len(not_already_sorted)} in this session.')
    show_window_with_keyboard_input(not_already_sorted, already_sorted, session_name, data_mode, annotator, ui_verbosity, n_bins)


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

    elif args.convert_test_imgs_to_png:  # will probably no longer be used
        data_prep.convert_test_imgs_to_png()

    elif args.convert_to_png:
        if args.image_list == 'data':
            for image_folder in ['test_imgs_dir', 'train_imgs_dir']:
                print(f'Doing for: {image_folder}')
                convert_imgs_to_png(source_dir=globals.params[image_folder],
                                    dest_dir=f'{globals.params[image_folder]}_png')

        elif args.image_list == 'results':  # only supports the perfectly sorted list for now
            image_list = helper.read_file_to_list(globals.params['sorted'])
            # print('read list:', image_list)
            save_path = os.path.join('..', 'output_visualized', 'sorted_imgs_png')
            helper.make_dir_if_not_exists(save_path)
            image_list_to_png(image_list, save_path=save_path)

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

    # elif args.session_name == 'split':
    #     split_sorted_list_to_bins(args.n_bins)  # no need to indicate annotator

    else:  # sort, variability, and split
        # requiring annotator name except for splitting
        if args.session_name != 'split' and args.annotator is None:
            message = 'Please provide annotator name using the --annotator argument'
            show_visual_error("Arguments specified incorrectly", message)
            exit(1)  # unsuccessful exit

        # set paths for train data
        if args.data_mode == 'train' or args.session_name == 'split':
            globals.params['img_registry'] = os.path.join('..', 'data', 'train_img_registry.txt')
            train_out_path = os.path.join(globals.params['output_path'], 'output_train')  # outputs/output_train
            globals.params['output_path'] = train_out_path
            globals.params['sorted'] = os.path.join(train_out_path, 'sorted.txt')
            globals.params['discarded'] = os.path.join(train_out_path, 'discarded.txt')
            globals.params['aborted'] = os.path.join(train_out_path, 'aborted.txt')
            globals.params['error'] = os.path.join(train_out_path, 'error.txt')
            globals.params['ratings'] = os.path.join(train_out_path, 'ratings.txt')

        # special checks and set paths for test data and variability check
        if args.data_mode == 'test':
            if not args.new and not args.already:  # one of the arguments should be specified
                message = 'Please use argument --new if it is the first time you are rating the images, or --already if you have already rated some images.'
                show_visual_error("Arguments specified incorrectly", message)
                exit(1)

            annotator_out_path = os.path.join(globals.params['output_path'], f'output_{args.annotator}')  # outputs/output_Moein
            print(f'Checking output path for annotator: {args.annotator} and output path: "{annotator_out_path}" with respect to --new or --already')

            # checking for new annotator
            if args.new and os.path.exists(annotator_out_path):
                message = f'Another annotator with name {args.annotator} exists. Please choose a different name when using --annotator.'
                show_visual_error("Arguments specified incorrectly", message)
                exit(1)

            # checking for already annotator
            if args.already and not os.path.exists(annotator_out_path):
                message = f'No annotator with name: {args.annotator} found. Are you specifying your name correctly?'
                show_visual_error("Arguments specified incorrectly", message)
                exit(1)

            # arguments specified correctly - set path for rating test images (for train images we use the usual output path specified in globals)
            globals.params['output_path'] = annotator_out_path
            globals.params['sorted'] = os.path.join(annotator_out_path, 'sorted.txt')
            globals.params['discarded'] = os.path.join(annotator_out_path, 'discarded.txt')
            globals.params['aborted'] = os.path.join(annotator_out_path, 'aborted.txt')
            globals.params['error'] = os.path.join(annotator_out_path, 'error.txt')

            if args.session_name == 'sort':  # sort test
                globals.params['img_registry'] = os.path.join('..', 'data', 'test_img_registry.txt')
                globals.params['ratings'] = os.path.join(annotator_out_path, 'ratings.txt')

            elif args.session_name == 'variability_intra':  # variability
                globals.params['img_registry'] = os.path.join(annotator_out_path, 'variability_intra_registry.txt')
                globals.params['ratings'] = os.path.join(annotator_out_path, 'variability_intra_ratings.txt')

            elif args.session_name == 'variability_inter':
                globals.params['img_registry'] = os.path.join(annotator_out_path, 'variability_inter_registry.txt')
                globals.params['ratings'] = os.path.join(annotator_out_path, 'variability_inter_ratings.txt')

            else:
                raise NotImplementedError(f'In [main]: session_name not implemented.')

        log(f"\n\n\n\n{'#' * 150}", no_time=True)
        log(f'In [main]: Checking paths for annotator: {args.annotator} and output_path: "{globals.params["output_path"]}" done.\n'
            f"registry {globals.params['img_registry']}\n"
            f"output_path: {globals.params['output_path']}\n"
            f"sorted: {globals.params['sorted']}\n"
            f"discarded: {globals.params['discarded']}\n"
            f"aborted: {globals.params['aborted']}\n"
            f"error: {globals.params['error']}\n"
            f"ratings: {globals.params['ratings']}")
        log(f"{'#' * 150}", no_time=True)

        make_dir_if_not_exists(globals.params['output_path'])

        if args.session_name == 'split':  # splitting - no need to indicate annotator
            split_sorted_list_to_bins(args.n_bins)
        else:  # session for sorting/variability
            manage_sessions_and_run(args)


if __name__ == '__main__':
    main()
