import os

# ===== running the program in debug mode
debug = False
email_error = False

params = {
    "test_basenames": os.path.join('..', 'data', 'test_basenames.txt'),
    "train_basenames": os.path.join('..', 'data', 'train_basenames.txt'),

    "test_imgs_dir": os.path.join('..', 'data', 'test_imgs'),  # for test data
    "train_imgs_dir": os.path.join('..', 'data', 'train_imgs'),  # for train data

    "data_path": os.path.join('..', 'data'),

    "output_path_test": os.path.join('..', 'outputs_test'),
    "output_path_train": os.path.join('..', 'outputs_train'),

    "show_border_time": 100,  # in milliseconds
    "robust_levels": 2,
    "robust_min_length": 4,  # minimum length of sorted list/number of bins valid for doing ternary
    "bin_rep_type": 'random',  # or 'last': specifies how the bin representative should be chosen

    "variability_samples_percentage": 10,
    "max_imgs_per_session": 10000,
    "resize_factor": 4,
    "email_interval": None
}
