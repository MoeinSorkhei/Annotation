import os

# ===== running the program in debug mode
debug = False

# ===== the mode for showing the images
# mode = 'single'
mode = 'side_by_side'

params = {
    "imgs_dir": os.path.join('..', 'tmp', 'dicoms_very_limited'),
    "output_path": os.path.join('..', 'output'),
    "sorted_file": os.path.join('..', 'output', 'sorted_txt'),

    "resize_factor": 7,
    "email_interval": 100
}
