import os

# ===== running the program in debug mode
debug = False

# ===== the mode for showing the images
# mode = 'single'
# mode = 'side_by_side'

params = {
    "main_imgs_dir": os.path.join('..', 'tmp', 'dicoms_very_limited'),  # for test data
    "other_imgs_dir": os.path.join('..', 'tmp', 'dicoms_limited'),  # for train data

    "output_path": os.path.join('..', 'output'),
    "sorted": os.path.join('..', 'output', 'sorted.txt'),

    "comparisons": os.path.join('..', 'output', 'comparisons.txt'),
    "comparisons_structured": os.path.join('..', 'output', 'comparisons.json'),

    "max_imgs_per_session": 3,  # to be changed to 100 in real use
    "resize_factor": 7,
    "email_interval": 10
}
