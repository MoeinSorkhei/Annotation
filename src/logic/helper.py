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
    # files = os.listdir(imgs_dir)
    paths = []
    for base_path, _, filenames in os.walk(imgs_dir):
        for f in sorted(filenames):  # always read the files sorted by name
            img_abs_path = os.path.abspath(os.path.join(base_path, f))
            paths.append(img_abs_path)
    return paths


def log(string, no_time=False):
    # output_path = os.path.join('..', 'output')  # TO BE FIXED???
    output_path = globals.params['output_path']
    make_dir_if_not_exists(output_path)
    print(string)
    # append string to the file with date and time
    line = f'{string}\n' if no_time else f'[{strftime("%Y-%m-%d %H:%M:%S", gmtime())}] $ {string}\n'
    log_file = os.path.join(output_path, 'log.txt')
    with open(log_file, 'a') as file:
        file.write(line)


def save_rating(img_name, rate):
    # output_path = os.path.join('..', 'output')  # TO BE FIXED???
    output_path = globals.params['output_path']
    make_dir_if_not_exists(output_path)

    rate_file = os.path.join(output_path, f'rate={rate}.txt')
    with open(rate_file, 'a') as file:
        file.write(f'{img_name}\n')
    log(f'In [save_rating]: img name "{img_name}" appended to "{rate_file}"')


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






