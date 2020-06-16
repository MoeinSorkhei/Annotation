import os

# ===== running the program in debug mode
debug = False

# ===== the mode for showing the images
# mode = 'single'
# mode = 'side_by_side'

params = {
    "imgs_dir": os.path.join('..', 'tmp', 'dicoms_very_limited'),
    "output_path": os.path.join('..', 'output'),

    "comparisons": os.path.join('..', 'output', 'comparisons.txt'),
    "comparisons_structured": os.path.join('..', 'output', 'comparisons.json'),

    # "bin_1": {
    #     "file": os.path.join('..', 'output', 'bin_1.txt'),
    #     "sorted_file": os.path.join('..', 'output', 'bin_1_sorted.txt'),
    #
    #     "comparisons": os.path.join('..', 'output', 'bin_1_comparisons.txt'),
    #     "comparisons_structured": os.path.join('..', 'output', 'bin_1_comparisons.json')
    #
    # },

    "resize_factor": 7,
    "email_interval": 10
}
