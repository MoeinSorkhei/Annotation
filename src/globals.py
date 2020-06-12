import os


debug = False

slash = os.path.sep  # '/' for linux and '\' for Windows
sorted_file = '../output/sorted.txt'


params = {
    # "imgs_dir": f"..{slash}tmp{slash}dicoms",
    "imgs_dir": f"..{slash}tmp{slash}dicoms_very_limited",
    # "imgs_dir": f"..{slash}tmp{slash}dicoms_limited_real_name",
    "output_path": f"..{slash}output",

    # "img_size": (256, 256),
    "resize_factor": 7,
    # "img_size": (512, 512),
    "email_interval": 100
}
