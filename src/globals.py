import os

# ===== running the program in debug mode
debug = False

params = {
    "registry_file": os.path.join('..', 'data', 'img_registry_ddsm.txt'),
    "test_imgs_renamed_dir": os.path.join('..', 'data', 'test_imgs_renamed'),

    "test_imgs_dir": os.path.join('..', 'data', 'test_imgs'),  # for test data
    # "test_imgs_dir": os.path.join('..', 'data', 'test_imgs_resized'),  # for test data
    "train_imgs_dir": os.path.join('..', 'data', 'train_imgs'),  # for train data
    # "train_imgs_dir": os.path.join('..', 'data', 'train_imgs_resized'),  # for train data

    "ks_csv_file": os.path.join('..', 'data', 'csv_files', 'data_ks_all_200630.csv'),
    "nonKS_csv_file": os.path.join('..', 'data', 'csv_files', 'data_nonks_all_200630.csv'),

    "ddsm_mass": os.path.join('..', 'data', 'ddsm', 'mass_case_description_train_set.csv'),
    "ddsm_calc": os.path.join('..', 'data', 'ddsm', 'calc_case_description_train_set.csv'),

    "ks_db_path": os.path.join('..', 'data', 'ks_db.sqlite'),
    "db_path": os.path.join('..', 'data', 'database.sqlite'),

    "output_path": os.path.join('..', 'output'),
    "data_path": os.path.join('..', 'data'),
    "sorted": os.path.join('..', 'output', 'sorted.txt'),
    "discarded": os.path.join('..', 'output', 'discarded.txt'),
    "aborted": os.path.join('..', 'output', 'aborted.txt'),
    "ratings": os.path.join('..', 'output', 'ratings.txt'),

    "show_border_time": 300,  # in seconds
    "robust_levels": 2,
    "robust_min_length": 4,  # minimum length of sorted list/number of bins valid for doing ternary
    "bin_rep_type": 'random',  # or 'last': specifies how the bin representative should be chosen

    "max_imgs_per_session": 10,
    "resize_factor": 3,
    "email_interval": None
}
