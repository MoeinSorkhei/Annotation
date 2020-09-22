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

    "ks_csv_file": {
        'density': os.path.join('..', 'data', 'csv_files', 'density', 'density_combined.csv'),
        'diagnosis': os.path.join('..', 'data', 'csv_files', 'diagnosis', 'data_ks_all_200630.csv')
    },

    "nonKS_csv_file": {
        'density': os.path.join('..', 'data', 'csv_files', 'density', 'nonKS_BFT_RCC_FirstCancer_Images_20190702_merged'),
        'diagnosis': os.path.join('..', 'data', 'csv_files', 'diagnosis', 'data_nonks_all_200630.csv')
    },

    "ddsm_mass": os.path.join('..', 'data', 'ddsm', 'mass_case_description_train_set.csv'),
    "ddsm_calc": os.path.join('..', 'data', 'ddsm', 'calc_case_description_train_set.csv'),

    # "db_path": os.path.join('..', 'data', 'databases'),
    "ks_db_path": {
        'density': os.path.join('..', 'data', 'databases', 'ks_density.sqlite'),
        'diagnosis': os.path.join('..', 'data', 'databases', 'ks_diagnosis.sqlite')
    },

    "data_path": os.path.join('..', 'data'),
    "output_path": os.path.join('..', 'outputs'),  # generic output_path, will be modified in the program
    # default paths for sort train, modified in main for other modes
    # "registry": os.path.join('..', 'data', 'train_img_registry.txt'),
    # "sorted": os.path.join('..', 'output', 'sorted.txt'),
    # "discarded": os.path.join('..', 'output', 'discarded.txt'),
    # "aborted": os.path.join('..', 'output', 'aborted.txt'),
    # "ratings": os.path.join('..', 'output', 'ratings.txt'),
    # "error": os.path.join('..', 'output', 'error.txt'),
    # "output_path": os.path.join('..', 'output'),
    #     "sorted": os.path.join('..', 'output', 'sorted.txt'),
    #     "discarded": os.path.join('..', 'output', 'discarded.txt'),
    #     "aborted": os.path.join('..', 'output', 'aborted.txt'),
    #     "ratings": os.path.join('..', 'output', 'ratings.txt'),
    #     "error": os.path.join('..', 'output', 'error.txt'),

    "show_border_time": 300,  # in milliseconds
    "robust_levels": 2,
    "robust_min_length": 4,  # minimum length of sorted list/number of bins valid for doing ternary
    "bin_rep_type": 'random',  # or 'last': specifies how the bin representative should be chosen

    "variability_samples_percentage": 10,
    "max_imgs_per_session": 10,
    "resize_factor": 3,
    "email_interval": None
}
