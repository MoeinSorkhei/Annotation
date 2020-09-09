import csv
import matplotlib.pyplot as plt
import sqlite3
import os
import pandas as pd
import globals
import random
from . import helper


# CSV files attributes - the nonKS data does not have basename
attributes = [
        'FileAnalyzed',  # 0
        'Manufacturer',  # 1
        'Laterality',  # 2
        'ViewPosition',  # 3
        'BreastArea_sqcm_',  # 4
        'DenseArea_sqcm_',  # 5
        'BreastDensity___',  # 6
        'basename'  # 7
]


def read_csv_file(filename):
    delimiter = ';' if 'density_combined.csv' in filename else ','

    with open(filename) as f:
        reader = csv.reader(f, delimiter=delimiter)
        lines = [row for row in reader]
    return lines


def combine_csv_files(verbose=False, also_return_separately=False):
    ks_file, non_ks_file = globals.params['ks_csv_file'], globals.params['nonKS_csv_file']
    ks_rows = read_csv_file(ks_file)[1:]
    non_ks_rows = read_csv_file(non_ks_file)[1:]

    if verbose:
        print(f'ks_file has len: {len(ks_rows):,} - nonKS file has len: {len(non_ks_rows):,}')

    if also_return_separately:
        return ks_rows + non_ks_rows, ks_rows, non_ks_rows
    return ks_rows + non_ks_rows


def draw_hist_from_csv(csv_file, features, main_att, sep, plot_labels, save_path=None):
    df = pd.read_csv(csv_file, sep=sep, engine='python')  # data frame

    # now supports only two attributes
    if len(features.keys()) == 2:
        keys = list(features.keys())
        vals = list(features.values())
        df = df.loc[(df[keys[0]] == vals[0]) & (df[keys[1]] == vals[1])]

    else:
        raise NotImplementedError

    df = df[main_att]
    print(f'df extracted with len: {df.size}')
    draw_hist(df.to_numpy(), plot_labels, save_path)


def draw_hist(values, labels, save_path, count_or_prob='count', logscale=False):
    plt.clf()

    vertical_is_prob = count_or_prob == 'prob'
    plt.hist(values, density=vertical_is_prob, bins=100)  # `density=False` would make counts

    if logscale:
        plt.xscale('log')

    # x label and y label and save to
    plt.xlabel(labels['x_label'])
    plt.ylabel(labels['y_label'])

    if save_path:
        plt.savefig(save_path)
    else:
        plt.show()


def density_hist(densities, view, filename):
    plt.clf()
    count_or_prob = 'Count'
    logscale = True

    plt.hist(densities, density=count_or_prob == 'Probability', bins=100)  # `density=False` would make counts

    if logscale:
        plt.xscale('log')

    plt.xlabel(f'{view} Log Density percent' if logscale else f'{view} Density percent')
    plt.ylabel(count_or_prob)

    save_to = f'../tmp/figs/{filename} - {view} - {"log scale" if logscale else "linear"}.jpg'
    plt.savefig(save_to)


def read_attribute_from_csv(attribute):
    rows = combine_csv_files(verbose=True)
    index = attributes.index(attribute)
    values = [row[index] for row in rows]
    return values, rows


def read_breast_densities(view=None, limit_to=None, plot=True):
    ks_file, non_ks_file = globals.params['ks_csv_file'], globals.params['nonKS_csv_file']

    ks_rows = read_csv_file(ks_file)
    non_ks_rows = read_csv_file(non_ks_file)

    if view:  # consider only images with this view
        print(f'only considering rows with view: {view}')
        ks_rows = [row for row in ks_rows if row[3] == view]
        non_ks_rows = [row for row in non_ks_rows if row[3] == view]

    print(f'len ks_rows: {len(ks_rows):,}')
    print(f'len non_ks_rows: {len(non_ks_rows):,}')

    ks_densities = [float(row[6]) for row in ks_rows[1:]]  # exclude the first rwo which is the attributes
    non_ks_densities = [float(row[6]) for row in non_ks_rows[1:]]  # exclude the first rwo which is the attributes

    if limit_to:
        ks_densities = ks_densities[:limit_to]
        non_ks_densities = non_ks_densities[:limit_to]

    if plot:
        density_hist(ks_densities, view, filename='KS')
        density_hist(non_ks_densities, view, filename='nonKS')


def extract_stats():
    filenames, all_rows = read_attribute_from_csv('FileAnalyzed')
    basenames = [filename.split('_')[0] for filename in filenames]
    patient_ids = list(set(basenames))  # uniques

    print(f'len basenames: {len(basenames):,}')
    print(f'len patient_ids: {len(patient_ids):,}')
    print(f'average num of images per patient: {int(len(basenames) / len(patient_ids))}')

    # for i in range(len(basenames)):
    for i in range(100):
        patient_id = patient_ids[i]
        print(f'patient_id: {patient_id}')

        for j in range(len(basenames)):
            if basenames[j] == patient_id:
                print(f'found for j: {j}')
                print(all_rows[j])
                print('')
        input()


def prepare_for_db(data_source):
    csv_file = globals.params['ks_csv_file']['diagnosis']
    common_columns = ['patient', 'split', 'x_case',
                      'dicom_viewposition', 'x_cancer_laterality', 'dicom_imagelaterality',
                      'dicom_manufacturer', 'full_path_clio', 'x_diadate', 'dicom_studydate']

    if data_source == 'KS_diagnosis':
        db_path = globals.params['ks_db_path']['diagnosis']
        columns = common_columns
    else:  # not used
        db_path = os.path.join('..', 'data', 'databases', 'ks_diagnosis_complete.sqlite')
        columns = common_columns + ['x_cancer_laterality']

    # read the csv file
    sep = ';'
    df = pd.read_csv(csv_file, sep=sep, engine='python', usecols=columns)[columns]  # data frame, columns specified order

    # get contra-lateral for cancer
    df['x_cancer_laterality'] = [item[0] if (item == 'Left' or item == 'Right') else item for item in df['x_cancer_laterality']]  # convert Left -> L and Right -> R

    # get random side for healthy
    random.seed(0)  # to get the same sequence every time
    rand_sides = [random.choice(['L', 'R']) if df['x_case'][i] == 0 else '_' for i in range(len(df['patient']))]  # rand side for healthy
    df.insert(loc=df.columns.get_loc('dicom_imagelaterality') + 1, column='rand_side', value=rand_sides)  # insert after image laterality

    # add new column for converting exact study dates to study years
    diag_dates = df['x_diadate'].tolist()
    diag_years = [str(date)[-4:] if str(date) != 'nan' else str(date) for date in diag_dates]

    study_dates = df['dicom_studydate'].tolist()
    study_years = [str(year)[:4] for year in study_dates]

    df['diag_year'] = diag_years
    df['study_year'] = study_years  # add column to data frame (at last column index)

    del df['dicom_studydate']  # delete unneeded columns
    del df['x_diadate']

    df_as_list = df.values.tolist()

    if data_source == 'KS_diagnosis':
        db_string = 'CREATE TABLE "KS_diagnosis" ' \
                '("patient" varchar, "split" varchar, "x_case" integer, ' \
                '"view" varchar, "cancer_laterality" varchar, "image_laterality" varchar, "rand_side" varchar,' \
                '"manufacturer" varchar, "full_path_clio" varchar, "diag_year" varchar, "study_year" varchar);'
        insert_command = 'INSERT INTO KS_diagnosis VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)'

    else:  # not used
        db_string = 'CREATE TABLE "KS_diagnosis_complete" ' \
                '("patient" varchar, "split" varchar, "x_case" integer, "view" varchar, "laterality" varchar, "manufacturer" varchar, ' \
                '"cancer_laterality" varchar, "diag_year" varchar, "study_year" varchar);'
        insert_command = 'INSERT INTO KS_diagnosis_complete VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'

    return df_as_list, db_path, db_string, insert_command


def csv_to_db(data_source, recreate=False):
    df_as_list, db_path, db_string, insert_command = prepare_for_db(data_source)

    if os.path.exists(db_path):
        if recreate:
            os.remove(db_path)
            print('Previous database destroyed')
        else:
            print('Database already exists. Terminating...')
            return
    helper.make_dir_if_not_exists(os.path.split(db_path)[0])  # make the directory

    con = sqlite3.Connection(db_path)
    cur = con.cursor()

    # create database
    cur.execute(db_string)
    print('Database created successfully')

    # insert items
    cur.executemany(insert_command, df_as_list)
    print('Inserted into database successfully')

    cur.close()
    con.commit()
    con.close()


def create_ddsm_query(mass_or_calc, left_or_right, view, attribute, value, limit=40, exclude_list=None):
    query_file = f'../data/ddsm/queries/{mass_or_calc}_{left_or_right}_{view}/{attribute}/{attribute}={value}.txt'
    with open(query_file) as f:
        lines = f.read().splitlines()
    print(f'In [create_ddsm_query]: len lines: {len(lines)}')

    subject_ids = [query_to_subject_id(mass_or_calc, patient_id, left_or_right, view) for patient_id in lines
                   if patient_id not in exclude_list]
    print(f'In [create_ddsm_query]: len subject_ids before applying limit: {len(subject_ids)}')

    subject_ids = subject_ids[:limit]
    query = ','.join(subject_ids)

    print(query)
    return query


def query_to_subject_id(mass_or_calc, patient_id, left_or_right, view):
    subject_id = f'{mass_or_calc}-Training_{patient_id}_{left_or_right}_{view}'
    return subject_id

