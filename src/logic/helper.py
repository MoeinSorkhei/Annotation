import os
import json


def read_params(params_path):
    with open(params_path, 'r') as f:  # reading params from the json file
        parameters = json.load(f)
    return parameters


def get_files_paths(imgs_dir):
    # files = os.listdir(imgs_dir)
    paths = []
    for base_path, _, filenames in os.walk(imgs_dir):
        for f in sorted(filenames):
            img_abs_path = os.path.abspath(os.path.join(base_path, f))
            paths.append(img_abs_path)
            # print(img_abs_path)
            # yield os.path.abspath(os.path.join(base_path, f))
    return paths
