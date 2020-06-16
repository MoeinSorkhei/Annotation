import os

# ===== running the program in debug mode
debug = False

# ===== the mode for showing the images
# mode = 'single'
# mode = 'side_by_side'

params = {
    "imgs_dir": os.path.join('..', 'tmp', 'dicoms_very_limited'),
    "output_path": os.path.join('..', 'output'),
    "sorted": os.path.join('..', 'output', 'sorted.txt'),

    "comparisons": os.path.join('..', 'output', 'comparisons.txt'),
    "comparisons_structured": os.path.join('..', 'output', 'comparisons.json'),

    "max_imgs_per_session": 10,  # to be changed to 100 in real use
    "resize_factor": 7,
    "email_interval": 10
}
