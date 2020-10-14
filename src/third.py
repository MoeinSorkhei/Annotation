from copy import deepcopy
from logic import *
import random
import argparse


# Moein
PATH1 = '/Users/user/PycharmProjects/Annotation/data_local/extracted_train_01_05'
PATH2 = '/Volumes/BOOTCAMP/Users/moein/Desktop/Annotation/Train data/extracted_train_06_10'


def parse_args():
    parser = argparse.ArgumentParser(description='Annotation tool')
    parser.add_argument('--copy_common', action='store_true')
    parser.add_argument('--sanity', action='store_true')
    parser.add_argument('--all', action='store_true')  # for sanity
    parser.add_argument('--bins_exist', action='store_true')
    parser.add_argument('--prep_bins', action='store_true')
    parser.add_argument('--vis_bins', action='store_true')
    parser.add_argument('--annotator', type=str)
    return parser.parse_args()


def copy_common_imgs():
    total_list = files_with_suffix(PATH1, '.dcm') + files_with_suffix(PATH2, '.dcm')
    common_list = read_file_to_list(os.path.join('..', 'data_local', 'common_imgs.txt'))

    print('len total list:', len(total_list))
    print('len common list:', len(common_list))

    from shutil import copyfile
    count = 0
    for filename in total_list:
        pure = pure_name(filename)
        if pure in common_list:
            copyfile(src=filename, dst=os.path.join(globals.params['train_imgs_dir'], pure))
            count += 1
            if count % 50 == 0:
                print(f'Copied {count} files')


def dicoms_sanity_train(all_imgs):
    if all_imgs:
        list1 = files_with_suffix(PATH1, '.dcm')
        list2 = files_with_suffix(PATH2, '.dcm')
        total_list = list1 + list2
    else:
        total_list = files_with_suffix(globals.params['train_imgs_dir'], '.dcm')

    print('total len:', len(total_list))
    counts = 0
    for i_file, filename in enumerate(total_list):
        try:
            dataset = pydicom.dcmread(filename)
        except:
            print('Exception for file:', filename)
            counts += 1
        if i_file % 500 == 0:
            print('Read for file:', i_file, ' => OK')
    print('Total errors:', counts)


def confirm_bin_imgs_exist(annotator):
    globals.params['output_path'] = os.path.join('..', 'outputs_train', f'output_{annotator}')
    _, imgs = all_imgs_in_all_bins()
    print('all bin images are:', len(imgs))
    existence = [os.path.isfile(img) for img in imgs]
    print('Existence:', all(existence))


def prepend_path_to_bins(annotator):
    output_path = os.path.join('..', 'outputs_train', f'output_{annotator}')
    for i in range(12):
        bin_file = os.path.join(output_path, f'bin_{i}.txt')
        files = read_file_to_list(bin_file)  # pure names
        files = [os.path.join(os.path.abspath(globals.params['test_imgs_dir']), f) for f in files]  # abs paths
        write_list_to_file(files, bin_file)
        print('Appended path to names in file:', bin_file)


def visualize_bins(annotator, bins_list):
    output_path = os.path.join('..', 'outputs_train', f'output_{annotator}')
    for i_bin in bins_list:
        bin_img_list = read_file_to_list(os.path.join(output_path, f'bin_{i_bin}.txt'))
        vis_path = os.path.join('..', 'data_local', f'bins_visualized_{annotator}', f'bin_{i_bin}')
        make_dir_if_not_exists(vis_path, verbose=False)
        image_list_to_png(bin_img_list, vis_path,)


if __name__ == '__main__':
    args = parse_args()
    if args.copy_common:  # python third.py --copy_common
        copy_common_imgs()

    elif args.prep_bins:
        assert args.annotator is not None
        prepend_path_to_bins(args.annotator)

    elif args.bins_exist:  # python third.py --bin_exist --annotator Moein
        assert args.annotator is not None
        confirm_bin_imgs_exist(args.annotator)

    elif args.sanity:  # python third.py --sanity --all
        dicoms_sanity_train(all_imgs=args.all)

    elif args.vis_bins:
        assert args.annotator is not None
        visualize_bins(args.annotator, list(range(12)))

    else:
        print('No argument specified')
