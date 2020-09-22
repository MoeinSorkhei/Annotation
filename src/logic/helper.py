import os
import json
from time import gmtime, strftime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import glob
import datetime
from shutil import copyfile
import random
import shutil

import globals


# ========== very generic functions
def read_params(params_path):
    with open(params_path, 'r') as f:  # reading params from the json file
        parameters = json.load(f)
    return parameters


def make_dir_if_not_exists(directory, verbose=True):
    if not os.path.isdir(directory):
        os.makedirs(directory)
        if verbose:
            print(f'In [make_dir_if_not_exists]: created path "{directory}"')


def multi_log(to_be_logged):
    for string in to_be_logged:
        log(string)


def log(string, no_time=False):
    output_path = globals.params['output_path']
    make_dir_if_not_exists(output_path)
    print(string)
    # append string to the file with date and time
    line = f'{string}\n' if no_time else f'[{get_datetime(raw=True)}] $ {string}\n'
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
    log('________________________________________________________________\n\n', no_time=True)


def read_file_to_list(filename):
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
    log(f'In [insert_to_list]: Now sorted list has len: {len(lst)}')


def shorten_file_name(filename):
    if len(filename) < 10:
        return filename
    else:
        return '...' + filename[-15:]


def get_all_dicom_files(img_folder):
    return glob.glob(f'{img_folder}/**/*.dcm', recursive=True)  # it assumes '/' path separator


def get_datetime(raw=False, underscored=False):
    if underscored:
        return datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    elif raw:
        return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return datetime.datetime.now().strftime("%Y-%m-%d at %H:%M:%S")


# ========== functions for saving/reading results
def write_sorted_list_to_file(lst):
    sorted_filename = globals.params['sorted']

    with open(sorted_filename, 'w') as f:
        for item in lst:
            f.write(f'{item}\n')
    log(f'In [write_sorted_list_to_file]: wrote sorted list to {sorted_filename}: done \n')

    if globals.debug:
        print_list(lst)


def save_rating(left_img, right_img, rate, annotator, timestamp):
    rate_file = globals.params['ratings']
    with open(rate_file, 'a') as f:
        string = f'{left_img} $ {right_img} $ {rate} $ {annotator} $ {timestamp}'
        f.write(f'{string}\n')


def remove_last_rating():
    rate_file = globals.params['ratings']
    remove_last_line_from_file(rate_file)


def remove_last_aborted():
    aborted_file = globals.params['aborted']
    remove_last_line_from_file(aborted_file)


def remove_last_line_from_file(filename):
    lines = read_file_to_list(filename)
    lines = lines[:-1]
    write_list_to_file(lines, filename)


def _parse_ratings():
    ratings_file = globals.params['ratings']
    ratings = read_file_to_list(ratings_file)

    parsed_ratings = []
    for rating in ratings:
        if rating.startswith('#'):  # this is separator between sessions
            continue
        left_file, right_file, rate, annotator, timestamp = rating.split('$')
        parsed_ratings.append((left_file.strip(), right_file.strip(), rate.strip(), annotator.strip(), timestamp.strip()))
    return parsed_ratings


def calc_variability_acc(variability_registry_file, variability_ratings_file):
    variability_ratings = read_file_to_list(variability_ratings_file)
    original_ratings = read_file_to_list(variability_registry_file)
    consistent_rates = 0
    for var_rating in variability_ratings:
        # get the original rating for the same "left $ right" file
        orig_rating = [item for item in original_ratings if item.startswith(left_right_substr(var_rating))][0]
        if parsed(var_rating, '$')[2] == parsed(orig_rating, '$')[2]:
            consistent_rates += 1
    acc = consistent_rates / len(variability_ratings)
    print(f'In [calc_variability_acc]: consistent_rates: {consistent_rates} of {len(variability_ratings)} ==> accuracy:', acc)
    return acc


def sample_ratings(orig_rating_file, variability_registry_file):
    ratings_list = read_file_to_list(orig_rating_file)
    ratings_list = [rating for rating in ratings_list if not rating.startswith('#')]  # remove session the separators
    print(f'In [sample_ratings]: original ratings list of file: "{orig_rating_file}" has len: {len(ratings_list)}')

    unique_extracted = []
    for rating in ratings_list:
        left_and_right = left_right_substr(rating)
        if not any([left_and_right in item for item in unique_extracted]):
            unique_extracted.append(rating)

    print(f'In [sample_ratings]: unique ratings list has len: {len(unique_extracted)}')
    n_samples = int((globals.params['variability_samples_percentage'] / 100) * len(ratings_list))

    print('In [sample_ratings]: Number of ratings to be sampled:', n_samples)
    samples = random.sample(unique_extracted, n_samples)

    write_list_to_file(samples, variability_registry_file)
    print(f'In [sample_ratings]: wrote sample ratings to: "{variability_registry_file}"')


def left_right_substr(string):
    # given a string like "2.dcm $ 33.dcm $ 9 $ Moein $ 2020-09-22_09:23:22", it returns "2.dcm $ 33.dcm"
    left, right = parsed(string, '$')[:2]
    return f'{left} $ {right}'


def parsed(string, character):
    return [item.strip() for item in string.split(character)]


def get_rate_if_already_exists(left_file, right_file):
    parsed_ratings = _parse_ratings()
    for record in parsed_ratings:
        if record[0] == left_file and record[1] == right_file:
            return record[2]  # the rate
    return None


def email_results():
    # output_path = globals.params['output_path']
    # fromaddr = "m.moein.sorkhei@gmail.com"
    # toaddr = "m.moein.sorkhei@gmail.com"
    fromaddr = "kthannotation@gmail.com"
    toaddr = "kthannotation@gmail.com"

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

    # creating zip file from output folder
    dirname = os.path.join('..', 'outputs')  # static address, the whole output folder
    zipped = os.path.join('..', 'outputs')  # it adds the .zip extension
    shutil.make_archive(zipped, 'zip', dirname)

    # for file_name in os.listdir(output_path):
    #     file_path = os.path.join(output_path, file_name)

    zipped_filepath = f'{zipped}.zip'
    attachment = open(zipped_filepath, "rb")
    part = MIMEBase('application', "octet-stream")
    part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header('Content-Disposition', 'attachment', filename='outputs.zip')
    msg.attach(part)

    # creates SMTP session
    s = smtplib.SMTP('smtp.gmail.com', 587)
    # start TLS for security
    s.starttls()
    # Authentication
    # s.login(fromaddr, "13747576")
    s.login(fromaddr, "eByte10Tonj##")
    # Converts the Multipart msg into a string
    text = msg.as_string()
    # sending the mail
    s.sendmail(fromaddr, toaddr, text)
    # terminating the session
    s.quit()
    # log(f'In [email_results]: emailed all the results\n')
    log(f'In [email_results]: creating zip file at: {zipped_filepath} and emailing: done.\n')





