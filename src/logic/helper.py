import os
import json
from time import gmtime, strftime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

import globals


# ========== very generic functions
def read_params(params_path):
    with open(params_path, 'r') as f:  # reading params from the json file
        parameters = json.load(f)
    return parameters


def make_dir_if_not_exists(directory):
    if not os.path.isdir(directory):
        os.makedirs(directory)
        print(f'In [make_dir_if_not_exists]: created path "{directory}"')


def multi_log(to_be_logged):
    for string in to_be_logged:
        log(string)


def log(string, no_time=False):
    output_path = globals.params['output_path']
    make_dir_if_not_exists(output_path)
    print(string)
    # append string to the file with date and time
    line = f'{string}\n' if no_time else f'[{strftime("%Y-%m-%d %H:%M:%S", gmtime())}] $ {string}\n'
    log_file = os.path.join(output_path, 'log.txt')
    with open(log_file, 'a') as file:
        file.write(line)


def split_to_lines(inp):
    if len(inp) == 3:
        string = f'({inp[0]}, \n{inp[1]}, {inp[2]})'
    else:
        string = f'({inp[0]}, {inp[1]})'
    return string


def pure_name(file_path):
    if file_path is None:
        return None
    return file_path.split(os.path.sep)[-1]


def print_list(sorted_list):
    log('________________________________________________________________', no_time=True)
    log(f'In [binary_search_step]: sorted_list:')
    for item in sorted_list:
        log(item, no_time=True)
    log('________________________________________________________________', no_time=True)


# def dict_to_lines(dictionary):
#     string = ''
#     for item in dictionary.items():
#


def print_comparisons_lists(comparisons):
    log('________________________________________________________________', no_time=True)
    log(f'In [print_comparisons_dict]: comparisons:', no_time=True)
    for img, lists in comparisons.items():
        log(f'{img}', no_time=True)
        for lst in lists:
            log(lst, no_time=True)
    log('________________________________________________________________', no_time=True)


# def read_file_to_list(file):
#     with open(file) as f:
#         lines = f.read().splitlines()
#     return lines


def read_file_to_list_if_exists(filename):
    lines = []
    if os.path.isfile(filename):
        with open(filename) as f:
            lines = f.read().splitlines()
    return lines


def write_list_to_file(lst, filename):
    with open(filename, 'w') as f:
        for item in lst:
            f.write(f'{item}\n')


def append_to_file(filename, item):
    with open(filename, 'a') as file:
        file.write(f'{item}\n')


def insert_to_list(lst, pos, item):
    lst.insert(pos, item)
    write_sorted_list_to_file(lst)


def shorten_file_name(filename):
    if len(filename) < 10:
        return filename
    else:
        return '...' + filename[-15:]


# ========== functions for saving/reading results
def read_comparison_lists():
    output_file = globals.params['comparisons_structured']  # output/comparisons.json

    comparison_lists = {}
    if os.path.isfile(output_file):
        with open(output_file, 'rb') as f:
            comparison_lists = json.load(f)
    return comparison_lists


def save_comparisons_list(comparisons):
    output_file = globals.params['comparisons_structured']  # output/comparisons.json

    # merged_dict = comparisons
    # merge with prev comparisons if they exist. If some values are in conflict, the new dict is given priority
    '''if os.path.isfile(output_file):
        prev_comparisons = read_comparison_lists()  # previous comparisons already in the json file
        merged_dict = {**comparisons, **prev_comparisons}'''

    with open(output_file, 'w') as f:
        json.dump(comparisons, f, indent=2)


def write_sorted_list_to_file(lst):
    sorted_filename = globals.params['sorted']

    with open(sorted_filename, 'w') as f:
        for item in lst:
            f.write(f'{item}\n')
    log(f'In [write_sorted_list_to_file]: wrote sorted list to {sorted_filename}: done \n')

    if globals.debug:
        print_list(lst)


def save_rating1(imgs, rate):
    # ======= for phase 1: where rate specifies the output file
    if len(imgs) == 1:
        raise NotImplementedError
        # filename = os.path.join(globals.params['output_path'], f'bin_{rate}')  # e.g., output/bin_1.txt
        # filename, _ = compute_file_paths_for_bin(rate=rate)  # WILL NO LONGER BE USED
        # result_as_str = imgs[0]

    # ======= for phase 2: where all the comparisons will be written to the same raw file (.txt)
    else:
        result_as_str = f'{imgs[0]} - {imgs[1]} - {rate}'
        filename = globals.params['comparisons']   # output/comparisons.txt

    with open(filename, 'a') as file:
        file.write(f'{result_as_str}\n')

    log_lines = imgs + [rate]
    log(f'In [save_rating]: case \n{split_to_lines(log_lines)} appended to "{filename}"\n')


def save_rating(left_img, right_img, rate):
    rate_file = globals.params['ratings']
    with open(rate_file, 'a') as f:
        string = f'{left_img} - {right_img} - {rate}'
        f.write(f'{string}\n')
    # log(f'In [save_rating]: saved the rate \n')


def remove_last_rating():
    rate_file = globals.params['ratings']
    remove_last_line_from_file(rate_file)
    # lines = read_file_to_list_if_exists(rate_file)
    # lines = lines[:-1]
    # write_list_to_file(lines, rate_file)
    # log(f'In [remove_last_rating]: removed tha last rate\n')


def remove_last_aborted():
    aborted_file = globals.params['aborted']
    remove_last_line_from_file(aborted_file)


def remove_last_line_from_file(filename):
    lines = read_file_to_list_if_exists(filename)
    lines = lines[:-1]
    write_list_to_file(lines, filename)


def email_results():
    output_path = globals.params['output_path']
    fromaddr = "m.moein.sorkhei@gmail.com"
    toaddr = "m.moein.sorkhei@gmail.com"

    # instance of MIMEMultipart
    msg = MIMEMultipart()
    # storing the senders email address
    msg['From'] = fromaddr
    # storing the receivers email address
    msg['To'] = toaddr
    # storing the subject
    msg['Subject'] = "Annotation Results"
    # string to store the body of the mail
    body = ""
    # attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    for file_name in os.listdir(output_path):
        file_path = os.path.join(output_path, file_name)
        attachment = open(file_path, "rb")

        part = MIMEBase('application', "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header('Content-Disposition', 'attachment', filename=file_name)
        msg.attach(part)

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)
    # start TLS for security
    s.starttls()
    # Authentication
    s.login(fromaddr, "13747576")
    # Converts the Multipart msg into a string
    text = msg.as_string()
    # sending the mail
    s.sendmail(fromaddr, toaddr, text)
    # terminating the session
    s.quit()
    log(f'In [email_results]: emailed all the results\n')





