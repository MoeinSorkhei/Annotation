from .helper import *
from .imaging import *
from . import helper
import logic
import random


def create_img_registry(img_folder, output_file):
    all_dicoms = glob.glob(f'{img_folder}/**/*.dcm', recursive=True)  # it assumes '/' path separator
    print(f'In [create_img_registry]: read {len(all_dicoms)} images from: "{img_folder}"')

    all_dicoms = [filename.replace(f'{img_folder}/', '') for filename in all_dicoms]  # get relative path from the base dir
    all_dicoms = sorted(all_dicoms)
    write_list_to_file(all_dicoms, output_file)
    print(f'In [create_img_registry]: creating image registry at: "{output_file}" done')


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
    helper.make_dir_if_not_exists(globals.params['output_path'])
    filename_list = ['10.dcm', '28.dcm', '33.dcm', '50.dcm', '78.dcm', '84.dcm']  # manually selected
    seed_list = [os.path.join(os.path.abspath(globals.params['test_imgs_dir']), filename) for filename in filename_list]
    helper.write_list_to_file(seed_list, globals.params['sorted'])
    log(f'Wrote seed list of len {len(seed_list)} to: "{globals.params["sorted"]}"')


def create_image_registry(data_mode):
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
