import argparse

from gui import *
from logic import *
from logic import data_prep


def read_args_and_adjust():
    parser = argparse.ArgumentParser(description='Annotation tool')
    parser.add_argument('--annotator', type=str)
    parser.add_argument('--other_annotator', type=str)
    parser.add_argument('--new', action='store_true')
    parser.add_argument('--already', action='store_true')
    parser.add_argument('--session_name', type=str, default='sort')
    parser.add_argument('--data_mode', type=str, default='test')
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


def manage_sessions_and_run(args):
    session_name = args.session_name
    data_mode = args.data_mode
    annotator = args.annotator

    ui_verbosity = 1  # default, least verbose
    if globals.debug:
        ui_verbosity = 4
    elif args.ui_verbosity is not None:
        ui_verbosity = args.ui_verbosity

    # image basenames should always be available
    if not os.path.isfile(globals.params[f'{args.data_mode}_basenames']):
        show_visual_error('', f'The basename file for {args.data_mode} data does not exists')
        exit(1)

    # now that the basename file exists, create image registry if not available - img registry is dependent on the laptop paths regardless of the annotator
    if not os.path.isfile(globals.params['img_registry']):
        data_prep.create_img_registry(args.data_mode)

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
        if session_name == 'variability_intra' or session_name == 'variability_inter':
            log(f'In [main]: all images for {session_name} are rated. The following is the result of variability checking:')
            calc_variability_acc(variability_registry_file=globals.params['img_registry'],
                                 variability_ratings_file=globals.params['ratings'])

        log(f'In [main]: not_already_sorted images are of len: 0 ==> Session is already complete. Terminating...')
        exit(0)

    # reduce the number of images for a session to a ore-defined number
    max_imgs_per_session = globals.params['max_imgs_per_session']
    not_already_sorted = not_already_sorted[:max_imgs_per_session]
    log(f'In [manage_sessions]: not_already_sorted reduced to have len: {len(not_already_sorted)} in this session.')
    show_window_with_keyboard_input(not_already_sorted, already_sorted, session_name, data_mode, annotator, ui_verbosity, n_bins)


def set_global_paths(session_name, data_mode, annotator=None, other_annotator=None, create_registry=False):
    if data_mode == 'train':
        globals.params['img_registry'] = os.path.join('..', 'data', 'train_img_registry.txt')
        train_out_path = os.path.join(globals.params['output_path'], 'output_train')  # outputs/output_train
        globals.params['output_path'] = train_out_path
        globals.params['sorted'] = os.path.join(train_out_path, 'sorted.txt')
        globals.params['discarded'] = os.path.join(train_out_path, 'discarded.txt')
        globals.params['aborted'] = os.path.join(train_out_path, 'aborted.txt')
        globals.params['error'] = os.path.join(train_out_path, 'error.txt')
        globals.params['ratings'] = os.path.join(train_out_path, 'ratings.txt')

    else:
        annotator_path = get_annotator_path(annotator)
        other_annotator_path = get_annotator_path(other_annotator)  # only needed for variability_inter

        globals.params['output_path'] = annotator_path
        globals.params['sorted'] = os.path.join(annotator_path, 'sorted.txt')
        globals.params['discarded'] = os.path.join(annotator_path, 'discarded.txt')
        globals.params['aborted'] = os.path.join(annotator_path, 'aborted.txt')
        globals.params['error'] = os.path.join(annotator_path, 'error.txt')

        if session_name == 'sort':  # sort test
            globals.params['img_registry'] = os.path.join('..', 'data', 'test_img_registry.txt')
            globals.params['ratings'] = os.path.join(annotator_path, 'ratings.txt')

        elif session_name == 'variability_intra':  # variability
            globals.params['img_registry'] = os.path.join(annotator_path, 'variability_intra_registry.txt')
            globals.params['ratings'] = os.path.join(annotator_path, 'variability_intra_ratings.txt')

        elif session_name == 'variability_inter':
            globals.params['img_registry'] = os.path.join(annotator_path, 'variability_inter_registry.txt')
            globals.params['ratings'] = os.path.join(annotator_path, 'variability_inter_ratings.txt')

        if create_registry:  # for variability checks - original rating file is also needed for creating registries
            if session_name == 'variability_intra':
                globals.params['orig_ratings'] = os.path.join(annotator_path, 'ratings.txt')
            else:
                globals.params['orig_ratings'] = os.path.join(other_annotator_path, 'ratings.txt')


def get_annotator_path(annotator):
    return os.path.join(globals.params['output_path'], f'output_{annotator}')  # outputs/output_Moein


def annotator_exists(annotator):
    return os.path.exists(get_annotator_path(annotator))


def check_args(args):
    if (args.session_name != 'split' or args.email_results) and args.annotator is None:
        message = 'Please provide annotator name using the --annotator argument'
        show_visual_error("Arguments specified incorrectly", message)
        exit(1)  # unsuccessful exit

    if args.session_name == 'sort' and args.data_mode == 'test':
        if not args.new and not args.already:  # one of the arguments should be specified
            message = 'Please use argument --new if it is the first time you are rating the images, or --already if you have already rated some images.'
            show_visual_error("Arguments specified incorrectly", message)
            exit(1)

        # checking for annotators paths
        annotator_out_path = get_annotator_path(args.annotator)
        if args.new and os.path.exists(annotator_out_path):
            message = f'Another annotator with name {args.annotator} exists. If you have already used the tool, use \n --already.'
            show_visual_error("Arguments specified incorrectly", message)
            exit(1)

        if args.already and not os.path.exists(annotator_out_path):
            message = f'No annotator with name: {args.annotator} found. Are you specifying your name correctly?'
            show_visual_error("Arguments specified incorrectly", message)
            exit(1)

    if args.session_name == 'variability_intra' or args.session_name == 'variability_inter':
        if args.new:
            message = f'Cannot be a --new radiologist for variability sessions'
            show_visual_error("Arguments specified incorrectly", message)
            exit(1)

        # check if annotator exists
        if not os.path.exists(get_annotator_path(args.annotator)):
            message = f'No annotator with name: {args.annotator} found. Are you specifying your name correctly?'
            show_visual_error("Arguments specified incorrectly", message)
            exit(1)

    if args.session_name == 'variability_inter' and \
            (args.other_annotator is None or not annotator_exists(args.other_annotator) or args.annotator == args.other_annotator):
        message = 'For inter_variability, a valid other_annotator should also be provided'
        show_visual_error("Arguments specified incorrectly", message)
        exit(1)  # unsuccessful exit


def main():
    args = read_args_and_adjust()
    check_args(args)  # make sure args are correct

    # emailing results
    if args.email_results:
        print('In [main]: emailing results...')
        logic.email_results(annotator=args.annotator, no_log=True)
        if globals.email_error:
            show_visual_error('Email error', 'Could not email the results. Please disable emailing option by using --no_email.')
        return

    # creating registries ONLY for variability - creation of test and train image registries are done in the first session
    if args.create_img_registry:
        set_global_paths(session_name=args.session_name, data_mode='test',
                         annotator=args.annotator, other_annotator=args.other_annotator, create_registry=True)  # other_annotator is None for intra

        print_global_paths(annotator=args.annotator)
        helper.sample_ratings(orig_rating_file=globals.params['orig_ratings'],
                              variability_registry_file=globals.params['img_registry'])

    # sort, variability rating, and split
    else:
        check_args(args)
        if args.data_mode == 'train' or args.session_name == 'split':
            data_mode = 'train'
        elif args.data_mode == 'test' or (args.session_name == 'variability_intra' or args.session_name == 'variability_inter'):
            data_mode = 'test'
        else:
            raise NotImplementedError('In [main]: Config not recognized for determining data_mode')

        set_global_paths(session_name=args.session_name, data_mode=data_mode, annotator=args.annotator)
        print_global_paths(annotator=args.annotator)
        make_dir_if_not_exists(globals.params['output_path'])

        if args.session_name == 'split':  # splitting - no need to indicate annotator
            split_sorted_list_to_bins(args.n_bins)
        else:  # session for sorting/variability
            manage_sessions_and_run(args)


if __name__ == '__main__':
    main()
