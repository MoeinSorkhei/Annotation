import os

# ===== running the program in debug mode
debug = False

# ===== the mode for showing the images
# mode = 'single'
# mode = 'side_by_side'

params = {
    "main_imgs_dir": os.path.join('..', 'data', 'dicoms_very_limited'),  # for test data
    "other_imgs_dir": os.path.join('..', 'data', 'dicoms_limited'),  # for train data

    "ks_csv_file": os.path.join('..', 'data', 'csv_files', 'data_ks_all_200630.csv'),
    "nonKS_csv_file": os.path.join('..', 'data', 'csv_files', 'data_nonks_all_200630.csv'),

    "ddsm_mass": os.path.join('..', 'data', 'csv_files', 'ddsm', 'mass_case_description_train_set.csv'),
    "ddsm_calc": os.path.join('..', 'data', 'csv_files', 'ddsm', 'calc_case_description_train_set.csv'),

    "ks_db_path": os.path.join('..', 'data', 'ks_db.sqlite'),
    "db_path": os.path.join('..', 'data', 'database.sqlite'),

    "output_path": os.path.join('..', 'output'),
    "sorted": os.path.join('..', 'output', 'sorted.txt'),
    "aborted": os.path.join('..', 'output', 'aborted.txt'),

    "comparisons": os.path.join('..', 'output', 'comparisons.txt'),
    "comparisons_structured": os.path.join('..', 'output', 'comparisons.json'),

    "search_type": 'robust',  # or 'normal'
    "robust_levels": 2,

    "max_imgs_per_session": 3,  # to be changed to 100 in real use
    "resize_factor": 7,
    "email_interval": 10
}
