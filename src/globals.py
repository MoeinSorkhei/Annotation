import os


slash = os.path.sep  # '/' for linux and '\' for Windows

params = {
    # "imgs_dir": f"..{slash}tmp{slash}dicoms",
    "imgs_dir": f"..{slash}tmp{slash}dicoms_limited",
    "output_path": f"..{slash}output",

    "img_size": (256, 256),
    # "img_size": (512, 512),
    "email_interval": 100
}
