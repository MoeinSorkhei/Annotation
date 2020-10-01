from .helper import *
from .imaging import *
from . import helper
import logic
import random


def rename_test_imgs(registry_file, test_imgs_folder, renamed_test_imgs_folder):
    img_registry = read_file_to_list(registry_file)
    make_dir_if_not_exists(renamed_test_imgs_folder)

    for i in range(len(img_registry)):
        source = os.path.join(test_imgs_folder, img_registry[i])
        renamed = os.path.join(renamed_test_imgs_folder, f'{i}.dcm')
        copyfile(src=source, dst=renamed)

        print(f'In [rename_test_imgs]: copied "{source}" to "{renamed}"')
    print('In [rename_test_imgs]: all done')


def convert_test_imgs_to_png():
    dicom_folder = globals.params['test_imgs_dir']
    png_folder = globals.params['test_imgs_dir'] + '_png'
    helper.make_dir_if_not_exists(png_folder)
    convert_imgs_to_png(dicom_folder, png_folder)

    # for renamed images if they exist
    if os.path.exists(globals.params['test_imgs_renamed_dir']):
        dicom_folder = globals.params['test_imgs_renamed_dir']
        png_folder = globals.params['test_imgs_renamed_dir'] + '_png'
        helper.make_dir_if_not_exists(png_folder)
        convert_imgs_to_png(dicom_folder, png_folder)


def make_seed_list():
    seed_list_basenames = [
        '4A7752346C424E4B3275595838797A6D5450506270513D3D_537153536F422F464D67367258752B663746777852414455364A6367436A4C48_20150129_1.dcm',
        '2B4A4748517956492B77423063754F7A7A6C625736513D3D_537153536F422F464D67344B6D3735393553587861514455364A6367436A4C48_20160607_2.dcm',
        '4E6B4E66536D594A674F2F6166332F354C732B5256513D3D_537153536F422F464D67343033324B4D52526E664A674455364A6367436A4C48_20150820_2.dcm',
        '5A757377306C54784A355A3078534D7348537A6D45773D3D_537153536F422F464D67376E415A5552585A4D706C774455364A6367436A4C48_20120611_1.dcm',
        '6A4E616D692B4B334A4A6862445737347162614A61673D3D_537153536F422F464D67377233564F686D425A4F4F674455364A6367436A4C48_20120629_4.dcm',
        '6D4B576170507A64373675426C4D66314B634D3571773D3D_537153536F422F464D673748424D2B716C496E3852414455364A6367436A4C48_20141007_2.dcm'
    ]
    seed_list = []
    for basename in seed_list_basenames:
        for filename in read_file_to_list(globals.params['img_registry']):
            if filename.endswith(basename):
                seed_list.append(filename)

    helper.write_list_to_file(seed_list, globals.params['sorted'])
    log(f'Wrote seed list of len {len(seed_list)} to: "{globals.params["sorted"]}"')


def create_img_registry(data_mode):
    basenames = read_file_to_list(globals.params[f'{data_mode}_basenames'])
    imgs_dir_abs = os.path.abspath(globals.params[f'{data_mode}_imgs_dir'])
    full_paths = [os.path.join(imgs_dir_abs, name) for name in basenames]

    registry_file = globals.params[f'img_registry']
    write_list_to_file(full_paths, registry_file)  # img_registry set in globals path
    log(f'Created image registry at: "{registry_file}": done')


def create_image_registry_prev(data_mode):
    print('Creating image registry for data_mode:', data_mode)
    if data_mode == 'test':
        img_lst = logic.get_dicom_files_paths(imgs_dir=globals.params['test_imgs_dir'])  # the dicom files
    else:
        img_lst = logic.get_dicom_files_paths(imgs_dir=globals.params['train_imgs_dir'])
    path = os.path.join(globals.params['data_path'], f'{data_mode}_img_registry.txt')

    write_list_to_file(img_lst, path)
    print(f'Saved image registry of len: {len(img_lst)} to: "{path}"')


def resize_data(image_dir, save_dir, new_width, new_height):
    all_dicoms = get_all_dicom_files(image_dir)
    for dicom in all_dicoms:
        resize_pixel_array(dicom, new_width, new_height, save_dir)


def get_size_stats(image_dir):
    all_dicoms = get_all_dicom_files(image_dir)
    all_widths, all_heights = [], []

    for dicom_file in all_dicoms:
        pixel_array_shape = dicom_as_dataset(dicom_file).pixel_array
        all_heights.append(pixel_array_shape.shape[0])
        all_widths.append(pixel_array_shape.shape[1])

    print(f'Mean width: {np.mean(np.array(all_widths))} - mean height: {np.mean(np.array(all_heights))}')
