from copy import deepcopy
from logic import *
import random
import argparse

CUSTOM_DENSITIES = [0, *list(range(5, 40, 5)), 40]


def parse_args():
    parser = argparse.ArgumentParser(description='Annotation tool')
    parser.add_argument('--other', action='store_true')
    parser.add_argument('--resize_data', action='store_true')
    parser.add_argument('--subset', type=str)  # for resize
    parser.add_argument('--place', type=str)  # remote or local
    parser.add_argument('--png', action='store_true')
    parser.add_argument('--assert_reg', action='store_true')
    parser.add_argument('--assert_bve', action='store_true')
    parser.add_argument('--dicoms_sanity', action='store_true')
    return parser.parse_args()


def hist(data_mode, only_draw_non_uniform=False, only_draw_orig=False):
    if data_mode == 'test_cancer':
        orig_list = get_density_list(query_csv='../data/databases/extracted_test_cancer.csv',
                                     density_csv='../data/csv_files/density_combined.csv')
        n_samples = 36
        x_label = 'Test - Cancer'

    elif data_mode == 'test_healthy':
        orig_list = get_density_list(query_csv='../data/databases/extracted_test_healthy.csv',
                                     density_csv='../data/csv_files/density_combined.csv')
        n_samples = 40
        x_label = 'Test - healthy'

    elif data_mode == 'train_cancer':
        orig_list = get_density_list(query_csv='../data/databases/extracted_train_cancer.csv',
                                     density_csv='../data/csv_files/density_combined.csv')
        x_label = 'Train - cancer'
        # n_samples = [21, 135, 137, 105, 69, 60, 58, 47, 93]  # all the cancer examples
        n_samples = 1000  # contain all samples

    elif data_mode == 'train_healthy':
        orig_list = get_density_list(query_csv='../data/databases/extracted_train_healthy.csv',
                                     density_csv='../data/csv_files/density_combined.csv')
        x_label = 'Train - healthy'
        # n_samples = [532, 1220, 1218, 1250, 1286, 1032, 835, 680, 1262]
        n_samples = [521, 1364, 1370, 1394, 1213,  984,  825,  652, 1088]

    else:
        raise NotImplementedError

    # non-uniform bins
    non_uniform = make_non_uniform(deepcopy(orig_list), CUSTOM_DENSITIES)

    if only_draw_orig:
        print('Drawing original density list...')
        draw_hist(list(range(102)), list_lens(orig_list), x_label)
        return

    if only_draw_non_uniform:
        print('Drawing non-uniform density list...')
        draw_hist(CUSTOM_DENSITIES + [101], list_lens(non_uniform), x_label)
        return

    # sample from non-uniform bins
    samples_list = sample_densities(deepcopy(non_uniform), n_samples)

    print(f'\ncustom_densities: {CUSTOM_DENSITIES}')
    print('non_uniform lens:', list_lens(non_uniform), ' - total len (bins):', len(non_uniform))
    print('samples_lst:', list_lens(samples_list), ' - total count:', total_len(samples_list))

    # draw_hist(CUSTOM_DENSITIES + [101], list_lens(samples_list), x_label)
    return samples_list


def extract_samples(data_mode):
    custom_densities = CUSTOM_DENSITIES + [101]
    if data_mode == 'test':
        caner_samples = hist('test_cancer')
        healthy_samples = hist('test_healthy')
        x_label = 'Test cancer + healthy'

    else:
        caner_samples = hist('train_cancer')
        healthy_samples = hist('train_healthy')
        x_label = 'Train cancer + healthy'

    random.seed(100)
    total_samples, cancer, healthy = [], [], []

    # first add cancer
    for i in range(len(caner_samples)):  # number of bins
        cancer.extend(caner_samples[i])
    random.shuffle(cancer)
    print('shuffled cancer')

    # then add healthy
    for i in range(len(healthy_samples)):
        healthy.extend(healthy_samples[i])
    random.shuffle(healthy)
    print('shuffled healthy')

    total_samples = cancer + healthy
    print('final len total_samples:', len(total_samples))

    # print(total_samples[:10])
    # input()

    write_list_to_file(total_samples, f'../data/databases/extracted_{data_mode}.txt')


def create_db():
    csv_file = '../data/csv_files/data_ks_cleaned.csv'
    db_path = '../data/databases/ks_cleaned.sqlite'
    csv_to_db(csv_file, db_path)


def create_image_basenames(data_mode):
    assert data_mode == 'test'
    extracted = read_file_to_list('../data_local/downloaded/extracted_test.txt')
    base_names = [os.path.split(filepath)[-1] for filepath in extracted]
    write_list_to_file(base_names, '../data/test_basenames.txt')


def adjust_clio_paths(data_mode):
    assert data_mode == 'test'
    txt_file = f'../data_local/databases/extracted_{data_mode}.txt'
    lst = read_file_to_list(txt_file)
    print('Read list of len:', len(lst))

    adjusted = [filename.replace('/clio/data/', '/storage/sorkhei/') for filename in lst]
    write_list_to_file(adjusted, txt_file)
    print('Wrote adjusted of len:', len(adjusted))


def check_train_files_unique(version):
    if version == 1:
        extracted = '../data_local/downloaded/extracted_train.txt'
        lst = read_file_to_list(extracted)
        lst = [filename.split('/')[-1] for filename in lst]

    if version == 2:
        lst = []
        for i in range(10):
            ind = f'{i + 1}' if i == 9 else f'0{i + 1}'
            lst.extend(read_file_to_list(f'../data_local/downloaded/extracted_train_{ind}.txt'))
        lst = [filename.split('/')[-1] for filename in lst]

    print('list len:', len(lst))
    print('len set:', len(set(lst)))
    print('equal len?', len(lst) == len(set(lst)))


def check_all_train_exist():
    for i in range(1, 6):  # todo: change the range to 10
        ind = i if i == 10 else f'0{i}'
        print('Checking for:', ind)

        the_list = read_file_to_list(f'../data_local/downloaded/extracted_train_{ind}.txt')
        the_list = pure_names(the_list, '/')
        the_list = prepend_to_paths(the_list, string=f'../data_local/downloaded/extracted_train_{ind}_resized/')

        # print(the_list[:10])
        # input()

        print('List len:', len(the_list))

        existence = [os.path.isfile(filename) for filename in the_list]
        print('All exist?', all(existence), '\n')


def split_train_extracted():
    extracted = '../data_local/downloaded/extracted_train.txt'
    lst = read_file_to_list(extracted)
    print('list len:', len(lst))

    splitted = np.array_split(lst, 10)
    for i, sublist in enumerate(splitted):
        filename = f'../data_local/downloaded/extracted_train_{i + 1}.txt'
        write_list_to_file(sublist, filename)
        print(f'Wrote list of len {len(sublist)} to {filename}')


def assert_existence(mode, data_mode):
    def _assert_pure_names_equality(l1, l2):
        l1 = [os.path.split(file)[-1] for file in l1]
        l2 = [os.path.split(file)[-1] for file in l2]
        print('assert equality result:', l1 == l2)
        assert l1 == l2

    assert data_mode == 'test'

    if mode == 'backup_equality':  # extracted with backup
        extracted = read_file_to_list('../data_local/downloaded/extracted_test.txt')
        backup = read_file_to_list('../data_local/databases/test/extracted_test_backup.txt')
        _assert_pure_names_equality(extracted, backup)

    elif mode == 'extracted_equality':
        extracted = read_file_to_list('../data_local/downloaded/extracted_test.txt')
        basenames = read_file_to_list('../data/test_basenames.txt')
        _assert_pure_names_equality(extracted, basenames)

    elif mode == 'img_registry':
        registry_list = read_file_to_list('../data/test_img_registry.txt')
        existence = all([os.path.isfile(reg_file) for reg_file in registry_list])
        print('img registry existence:', existence)


def resize_data(subset, resize_factor=2):
    if subset == 'test':
        save_dir = '/storage/sorkhei/resized_test'
        file_list = read_file_to_list('../data_local/downloaded/extracted_test.txt')
        raise NotImplementedError('Need refactoring the file_path before calling resize_pixel_array')

    else:  # e.g. extracted_train_01
        # source_dir = f'/storage/sorkhei/{subset}'
        save_dir = f'/storage/sorkhei/{subset}_resized'
        file_list = read_file_to_list(f'../data_local/downloaded/{subset}.txt')
        file_list = pure_names(file_list, sep='/')
        file_list = [f'/storage/sorkhei/{subset}/{filename}' for filename in file_list]

    print('File list has len:', len(file_list))
    # confirm all files exist
    assert all([os.path.isfile(filename) for filename in file_list])
    print('All files exists: OK')
    make_dir_if_not_exists(save_dir)

    for file_path in file_list:
        resize_pixel_array(file_path, resize_factor, save_dir)  # saves with purname in the save_dir folder


def convert_to_png(sorted_list_path, source_dir, dest_dir, op_sys, limit=None):
    sep = "\\" if op_sys == 'windows' else '/'

    the_list = read_file_to_list(sorted_list_path)
    if limit is not None:
        the_list = the_list[:limit]
    print('List len:', len(the_list))

    make_dir_if_not_exists(dest_dir)

    for i, filepath in enumerate(the_list):
        print(f'Reading image {i + 1} of list')
        if 'aborted' in sorted_list_path:  # to be removed
            filepath = parsed(filepath, '$')[0]

        pure = filepath.split(sep)[-1]
        print(f'pure name:', pure)

        sorted_pure = f'{i + 1} - {pure[:-4]}.png'  # also remove .dcm
        read_dicom_and_resize(os.path.join(source_dir, pure), save_to=os.path.join(dest_dir, sorted_pure))


def check_whole_train_data():
    folder_1 = '../data_local_downloaded/extracted_train_01_05'
    folder_2 = '/Volumes/BOOTCAMP/Users/moein/Desktop/Annotation/Train data/extracted_train_06_10'
    all_files_1 = helper.files_with_suffix(folder_1, '.dcm')
    all_files_2 = helper.files_with_suffix(folder_2, '.dcm')
    all_files = all_files_1 + all_files_2
    # then


def dicoms_sanity(subset, place):
    if subset == '01_05':
        for i in [1, 2, 3, 4, 5]:
            dicoms_sanity_subset(f'extracted_train_0{i}', place)
    elif subset == '06_10':
        for i in [6, 7, 8, 9]:
            dicoms_sanity_subset(f'extracted_train_0{i}', place)
        dicoms_sanity_subset(f'extracted_train_10', place)
    else:
        dicoms_sanity_subset(subset, place)


def dicoms_sanity_subset(subset, place):
    if place == 'remote':
        text_file = f'/home/sorkhei/Annotation/data_local/downloaded/{subset}.txt'
        prepend_text = f'/storage/sorkhei/{subset}/'
    else:
        text_file = f'../data_local/downloaded/{subset}.txt'
        prepend_text = f'../data_local/downloaded/{subset}_resized/'

    print('Reading files from:', text_file)
    files = read_file_to_list(text_file)
    files = pure_names(files, '/')
    files = prepend_to_paths(files, prepend_text)
    print('read file list of len:', len(files))

    counts = 0
    for filename in files:
        try:
            dataset = pydicom.dcmread(filename)
        except:
            print('Exception for file:', filename)
            counts += 1
    print('Total errors:', counts)


def dicoms_sanity_whole_train():
    path2 = '/Users/user/PycharmProjects/Annotation/data_local/downloaded/extracted_train_01_05'
    path1 = '/Volumes/BOOTCAMP/Users/moein/Desktop/Annotation/Train data/extracted_train_06_10'

    list1 = files_with_suffix(path1, '.dcm')
    list2 = files_with_suffix(path2, '.dcm')

    total_list = list1 + list2
    print('total len:', len(total_list))
    print('total uniques:', len(set(total_list)))
    input()

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


if __name__ == '__main__':
    # create_db()

    # cancer_ = hist(data_mode=['test_cancer', 'test_healthy', 'train_cancer', 'train_healthy'][2])  # index for test or train
    # healthy_ = hist(data_mode=['test_cancer', 'test_healthy', 'train_cancer', 'train_healthy'][3])
    #
    # draw_hist_stacked(CUSTOM_DENSITIES + [101], list_lens(cancer_), list_lens(healthy_),  # Note: 1. Make the label correct, 2. Comment draw_hist in hist()
    #                   x_label='Train cancer + healthy', legend_names=['cancer', 'healthy'])

    # extract_samples(data_mode='train')
    args = parse_args()

    if args.other:
        check_all_train_exist()
        # check_train_files_unique(version=2)
        # split_train_extracted()

    elif args.resize_data:  # needs --subset
        resize_data(args.subset)

    elif args.png:  # needs --subset
        if 'extracted_train' not in args.subset:
            raise NotImplementedError

        file = f'../data_local/downloaded/{args.subset}.txt'
        source = f'../data_local/downloaded/{args.subset}_resized'
        dest = f'../data_local/downloaded/{args.subset}_resized_visualized'
        os_sys = 'mac'
        limit = 10

        convert_to_png(file, source, dest, os_sys, limit)

    elif args.assert_bve:  # base v. extracted
        assert_existence('extracted_equality', 'test')

    elif args.assert_reg:
        assert_existence('img_registry', 'test')

    elif args.dicoms_sanity:  # needs --subset --place
        # dicoms_sanity(args.subset, args.place)
        dicoms_sanity_whole_train()

