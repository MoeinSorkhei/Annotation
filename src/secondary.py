from copy import deepcopy
from logic import *
import random
import argparse

CUSTOM_DENSITIES = [0, *list(range(5, 40, 5)), 40]


def parse_args():
    parser = argparse.ArgumentParser(description='Annotation tool')
    parser.add_argument('--resize_data', action='store_true')
    parser.add_argument('--png', action='store_true')
    parser.add_argument('--assert_reg', action='store_true')
    parser.add_argument('--assert_bve', action='store_true')
    parser.add_argument('--dicom_errors', action='store_true')
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


def resize_data(resize_factor=2):
    save_dir = '/storage/sorkhei/resized_test'
    file_list = read_file_to_list('../data_local/downloaded/extracted_test.txt')

    print('File list has len:', len(file_list))
    make_dir_if_not_exists(save_dir)

    for file_path in file_list:
        resize_pixel_array(file_path, resize_factor, save_dir)


def convert_to_png(sorted_list_path, source_dir, dest_dir, op_sys):
    # assert data_mode == 'test'
    # convert_imgs_to_png('../data_local/downloaded/test', '../data_local/test_imgs_png')
    sep = "\\" if op_sys == 'windows' else '/'

    sorted_list = read_file_to_list(sorted_list_path)
    print('Sorted list len:', len(sorted_list))

    make_dir_if_not_exists(dest_dir)

    for i, filepath in enumerate(sorted_list):
        print(f'Reading image {i + 1} of sorted list')

        if 'aborted' in sorted_list_path:  # to be removed
            filepath = parsed(filepath, '$')[0]

        pure = filepath.split(sep)[-1]
        print(f'pure name:', pure)

        sorted_pure = f'{i + 1} - {pure[:-4]}.png'  # also remove .dcm
        # print('sorted pure:', sorted_pure)
        # sorted_save_path = os.path.join(dest_dir, sorted_pure)
        # print('sorted save path:', os.path.join(dest_dir, sorted_pure))
        # input()

        read_dicom_and_resize(os.path.join(source_dir, pure), save_to=os.path.join(dest_dir, sorted_pure))


def count_dicom_errors():
    files = read_file_to_list('../data/test_img_registry.txt')
    print('read image regitry of len:', len(files))

    counts = 0
    for filename in files:
        try:
            dataset = pydicom.dcmread(filename)
        except:
            print('Excpetion for file:', filename)
            counts += 1
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
    # adjust_clio_paths(data_mode='test')
    # create_image_basenames('test')

    if args.resize_data:
        resize_data()

    elif args.png:
        convert_to_png('../test_results/output_Fredrik/old_aborted (2).txt',
                       source_dir='../data/test_imgs',
                       dest_dir='../test_results/output_Fredrik_aborted',
                       op_sys='windows')

    elif args.assert_bve:  # base v. extracted
        assert_existence('extracted_equality', 'test')

    elif args.assert_reg:
        assert_existence('img_registry', 'test')

    elif args.dicom_errors:
        count_dicom_errors()

