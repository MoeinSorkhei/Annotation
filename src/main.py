import argparse

import gui
import logic


def read_params_and_args():
    parser = argparse.ArgumentParser(description='Annotation tool')
    parser.add_argument('--imgs_dir', type=str)
    parser.add_argument('--output_path', type=str)

    arguments = parser.parse_args()
    params = logic.read_params('../params.json')

    return arguments, params


def adjust_params(args, params):
    if args.imgs_dir is not None:
        params['imgs_dir'] = args.imgs_dir

    if args.output_path is not None:
        params['output_path'] = args.output_path  # not used at the moment

    return params


def main():
    args, params = read_params_and_args()
    params = adjust_params(args, params)
    gui.show_window_with_keyboard_input(params)


if __name__ == '__main__':
    main()
