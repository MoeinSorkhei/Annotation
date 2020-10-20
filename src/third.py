from copy import deepcopy
from logic import *
import random
import argparse


# PATH1 = '../data_local/extracted_train_01_05'
# PATH2 = '../data_local/extracted_train_06_10'
PATH1 = os.path.join('..', 'data_local', 'extracted_train_01_05')
PATH2 = os.path.join('..', 'data_local', 'extracted_train_06_10')


# def get_train_paths(annotator):
#     if annotator == 'moein':
#         path1 = '/Users/user/PycharmProjects/Annotation/data_local/extracted_train_01_05'
#         path2 = '/Volumes/BOOTCAMP/Users/moein/Desktop/Annotation/Train data/extracted_train_06_10'
#
#     elif annotator == 'fredrik':
#         path1 = '/Users/fredrikstrand/Desktop/MammoAI Annotation/Annotation/data_local/extracted_train_01_05'
#         path2 = '/Users/fredrikstrand/Desktop/MammoAI Annotation/Annotation/data_local/extracted_train_06_10'
#
#     else:
#         raise NotImplementedError
#     return path1, path2


def parse_args():
    parser = argparse.ArgumentParser(description='Annotation tool')
    parser.add_argument('--copy_common', action='store_true')
    parser.add_argument('--sanity', action='store_true')
    parser.add_argument('--all', action='store_true')  # for sanity
    parser.add_argument('--bins_exist', action='store_true')
    parser.add_argument('--prep_bins', action='store_true')
    parser.add_argument('--vis_bins', action='store_true')
    parser.add_argument('--redistribute', action='store_true')
    parser.add_argument('--count_total', action='store_true')
    parser.add_argument('--annotator', type=str)
    return parser.parse_args()


def copy_common_imgs():
    # path1, path2 = get_train_paths(annotator)
    total_list = files_with_suffix(PATH1, '.dcm') + files_with_suffix(PATH2, '.dcm')
    common_list = read_file_to_list(os.path.join('..', 'data_local', 'common_imgs.txt'))

    print('len total list:', len(total_list))
    print('len common list:', len(common_list))

    print('waiting for input...')
    input()
    make_dir_if_not_exists(globals.params['train_imgs_dir'], verbose=False)

    from shutil import copyfile
    count = 0
    for filename in total_list:
        pure = pure_name(filename)
        if pure in common_list:
            copyfile(src=filename, dst=os.path.join(globals.params['train_imgs_dir'], pure))
            count += 1
            if count % 50 == 0:
                print(f'Copied {count} files')


def get_chunk_path(chunk_num):
    if chunk_num <= 5:
        return os.path.join('..', 'data_local', 'extracted_train_01_05', f'extracted_train_0{chunk_num}_resized')
    elif chunk_num < 10:
        return os.path.join('..', 'data_local', 'extracted_train_06_10', f'extracted_train_0{chunk_num}_resized')
    return os.path.join('..', 'data_local', 'extracted_train_06_10', f'extracted_train_10_resized')


def transfer_files(source_files_list, dest_folder):
    for i_file, source_filename in enumerate(source_files_list):
        dest_filename = os.path.join(dest_folder, pure_name(source_filename))
        # print('source_filename:', source_filename)
        # print('dest filename:', dest_filename)
        # input()
        shutil.move(source_filename, dest_filename)
        if (i_file % 50 == 0) or (i_file == len(source_files_list) - 1):
            print(f'Moving file {i_file + 1}: done')


def transfer_between_chunk(dest_chunk):
    source_chunk = 1
    source_chunk_path = get_chunk_path(source_chunk)
    dest_chunk_path = get_chunk_path(dest_chunk)

    source_chunk_files = files_with_suffix(source_chunk_path, '.dcm')
    dest_chunk_files = files_with_suffix(dest_chunk_path, '.dcm')
    print(f'Total files in source_chunk {source_chunk} is: {len(source_chunk_files)}')
    print(f'Total files in dest_chunk {dest_chunk} is: {len(dest_chunk_files)}')

    cancer_file = os.path.join('..', 'data_local', f'train_cancers_chunk{dest_chunk}.txt')
    cancer_list = prepend_to_paths(read_file_to_list(cancer_file), f'{source_chunk_path}{os.path.sep}')
    len_cancer = len(cancer_list)
    print(f'Cancer file: {cancer_file} has len: {len_cancer}')

    samples = random.sample(dest_chunk_files, len_cancer)
    print(f'Selected {len_cancer} files randomly from chunk path: {dest_chunk_path}')
    input()

    print(f'{"=" * 10} Transferring samples from chunk {dest_chunk}')
    transfer_files(source_files_list=samples, dest_folder=source_chunk_path)  # from other chunk to chunk 1
    input()

    print(f'{"=" * 10} Transferring cancers from chunk {source_chunk}')
    transfer_files(source_files_list=cancer_list, dest_folder=dest_chunk_path)  # from chunk 1 to other chunk
    input()

    print('All done')
    print(f'Now source chunk path {source_chunk_path} has len: {len(files_with_suffix(source_chunk_path, ".dcm"))}'
          f'\nand dest chunk path {dest_chunk_path} has len: {len(files_with_suffix(dest_chunk_path, ".dcm"))} \n\n')


def count_cancers(chunk_num):
    chunk_path = get_chunk_path(chunk_num)
    chunk_files_purenames = pure_names(files_with_suffix(chunk_path, '.dcm'), os.path.sep)
    train_cancers = read_file_to_list(os.path.join('..', 'data_local', 'train_cancers.txt'))
    count = sum([file in train_cancers for file in chunk_files_purenames])
    print(f'Path: {chunk_path} has {len(chunk_files_purenames)} files, cancer: {count}')


def count_total(with_sanity=True):
    total_files = pure_names(files_with_suffix(os.path.join('..', 'data_local', 'extracted_train_01_05'), '.dcm') +
                             files_with_suffix(os.path.join('..', 'data_local', 'extracted_train_06_10'), '.dcm'), os.path.sep)
    total_files = list(set(total_files))
    print('Total unique files:', len(total_files))
    print('_' * 50)

    for i in range(10):
        count_cancers(i + 1)
        if i % 2 == 1:
            print('\n')

    common_images = read_file_to_list(os.path.join('..', 'data_local', 'common_imgs.txt'))
    train_imgs = pure_names(files_with_suffix(globals.params['train_imgs_dir'], '.dcm'), sep=os.path.sep)
    existence_list = [file in train_imgs for file in common_images]
    print(f'train_imgs has len: {len(train_imgs)}, all common_imgs exists: {all(existence_list)}\n')

    if with_sanity:
        dicoms_sanity(all_imgs=True)


def distribute_cancers():
    transfer_between_chunk(dest_chunk=3)
    transfer_between_chunk(dest_chunk=5)
    transfer_between_chunk(dest_chunk=7)
    transfer_between_chunk(dest_chunk=9)
    count_total(with_sanity=True)


def dicoms_sanity(all_imgs):
    if all_imgs:
        # path1, path2 = get_train_paths(annotator)
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
            print('Sanity check for file:', i_file, ' => OK')
    print('Total errors:', counts)


def confirm_bin_imgs_exist(annotator):
    globals.params['output_path'] = os.path.join('..', 'outputs_train', f'output_{annotator}')
    _, imgs = all_imgs_in_all_bins()
    print('all bin images are:', len(imgs))
    existence = [os.path.isfile(img) for img in imgs]
    print('existence of all images in the bins:', all(existence))


def prepend_path_to_bins(annotator):
    n_bins = 8
    output_path = os.path.join('..', 'outputs_train', f'output_{annotator}')
    for i in range(n_bins):
        bin_file = os.path.join(output_path, f'bin_{i}.txt')
        files = read_file_to_list(bin_file)  # pure names
        files = [os.path.join(os.path.abspath(globals.params['test_imgs_dir']), f) for f in files]  # abs paths
        write_list_to_file(files, bin_file)
        print('Appended path to names in file:', bin_file)


def visualize_bins(annotator, bins_list):
    output_path = os.path.join('..', 'outputs_train', f'output_{annotator}')
    for i_bin in bins_list:
        bin_img_list = read_file_to_list(os.path.join(output_path, f'bin_{i_bin}.txt'))
        vis_path = os.path.join('..', 'data_local_me', f'bins_visualized_{annotator}_{len(bins_list)}bins', f'bin_{i_bin}')
        make_dir_if_not_exists(vis_path, verbose=False)
        image_list_to_png(bin_img_list, vis_path,)


def main():
    args = parse_args()

    if args.copy_common:   # python third.py --copy_common
        copy_common_imgs()

    elif args.redistribute:  # python third.py --redistribute
        distribute_cancers()

    elif args.count_total:  # python third.py --count_total
        count_total(with_sanity=True)  # confirm redistribution

    elif args.prep_bins:  # python third.py --prep_bins --annotator fredrik
        assert args.annotator is not None
        prepend_path_to_bins(args.annotator)
        confirm_bin_imgs_exist(args.annotator)

    # ========= not so important
    elif args.sanity:  # python third.py --sanity --all
        dicoms_sanity(all_imgs=args.all)

    elif args.vis_bins:
        assert args.annotator is not None
        visualize_bins(args.annotator, list(range(8)))

    else:
        print('No argument specified')


if __name__ == '__main__':
    main()
