import os
import json
from time import gmtime, strftime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders

import globals


def read_params(params_path):
    with open(params_path, 'r') as f:  # reading params from the json file
        parameters = json.load(f)
    return parameters


def make_dir_if_not_exists(directory):
    if not os.path.isdir(directory):
        os.makedirs(directory)
        print(f'In [make_dir_if_not_exists]: created path "{directory}"')


def get_files_paths(imgs_dir):
    paths = []
    for base_path, _, filenames in os.walk(imgs_dir):
        for f in sorted(filenames):  # always read the files sorted by name
            img_abs_path = os.path.abspath(os.path.join(base_path, f))
            paths.append(img_abs_path)
    return paths


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


def write_list_to_file(filename, lst):
    with open(filename, 'w') as f:
        for item in lst:
            f.write(f'{item}\n')


def split_to_lines(inp):
    if len(inp) == 3:
        string = f'({inp[0]}, \n{inp[1]}, {inp[2]})'
    else:
        string = f'({inp[0]}, {inp[1]})'
    return string


def pure_name(file_path):
    return file_path.split(os.path.sep)[-1]


def print_list(sorted_list):
    log('________________________________', no_time=True)
    log(f'In [binary_search_step]: sorted_list:')
    for item in sorted_list:
        log(item, no_time=True)
    log('________________________________', no_time=True)


def print_comparisons_dict(comparisons):
    print(f'In [print_comparisons_dict]: comparisons:')
    for img, v in comparisons.items():
        print(f'{img}')
        print(v[0])
        print(v[1])
        print()


def save_comparison_lists(comparisons):
    output_path = globals.params['output_path']  # TO BE FIXED
    make_dir_if_not_exists(output_path)
    output_file = os.path.join(output_path, 'comparison_sets.json')

    with open(output_file, 'w') as f:
        json.dump(comparisons, f, indent=2)

    # output_file = os.path.join(output_path, 'comparison_sets.pkl')
    # with open(output_file, 'wb') as f:
    #    pickle.dump(comparisons, file=f, protocol=0)  # protocol 0 for text


def read_comparison_lists():
    output_path = globals.params['output_path']
    output_file = os.path.join(output_path, 'comparison_sets.json')
    # output_file = os.path.join(output_path, 'comparison_sets.pkl')  # TO BE FIXED
    # with open(output_file, 'rb') as f:
    #    return pickle.load(f)
    with open(output_file, 'rb') as f:
        comparison_lists = json.load(f)
    return comparison_lists


def save_rating(imgs, rate):
    output_path = globals.params['output_path']
    make_dir_if_not_exists(output_path)

    if len(imgs) == 1:
        result_as_str = imgs[0]
        output_file = os.path.join(output_path, f'rate={rate}.txt')

    else:  # len(imgs) = 2:
        # DETERMINE THE OUTPUT FILE CORRECTLY
        result_as_str = f'{imgs[0]} - {imgs[1]} - {rate}'
        output_file = os.path.join(output_path, f'comparison.txt')

    with open(output_file, 'a') as file:
        file.write(f'{result_as_str}\n')

    log_lines = imgs + [rate]
    log(f'In [save_rating]: case \n{split_to_lines(log_lines)} appended to "{output_file}"\n')


def email_results():
    # output_path = os.path.join('..', 'output')  # TO BE FIXED???
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
    log(f'In [email_results]: emailed all the results')






