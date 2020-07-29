#!/bin/bash

# =====================  On my mac:
# test data
python3 main.py --annotator Moein --session_name sort --data_mode test --debug
# split
python3 main.py --annotator Moein --session_name split --n_bins 14 --debug
# train data
python3 main.py --annotator Moein --session_name sort --data_mode train --debug


# data preparation:
python3 main.py --resize_data
python3 main.py --make_seed_list



# ===================== actual run
# use --email_interval option
# use --max_imgs_per_session option
# use --resize_factor option


# ===================== On annotation laptop:
# test data
python main.py --annotator Moein --session_name sort --data_mode test --debug
# split
python main.py --annotator Moein --session_name split --n_bins 10 --debug
# train data
python main.py --annotator Moein --session_name sort --data_mode train --debug
