import csv
import matplotlib.pyplot as plt
import sqlite3
import os
import pandas as pd
import globals


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


def csv_to_db(data_source):
    if data_source == 'KS':
        csv_file = globals.params['ks_csv_file']
        columns = ['patient', 'x_case', 'x_diadate', 'split']
        sep = ';'

        db_path = globals.params['ks_db_path']

        db_string = 'CREATE TABLE "KS" ("patient" varchar, "x_case" integer, "x_diadate" varchar, "split" varchar);'
        insert_command = 'INSERT INTO patients VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)'

    elif data_source == 'nonKS':
        # csv_file = globals.params['nonKS_csv_file']
        # columns = None
        raise NotImplementedError

    elif data_source == 'ddsm_mass' or 'ddsm_calc':
        db_path = f'../data/ddsm/databases/{data_source}.sqlite'
        csv_file = globals.params[data_source]
        sep = ','

        # different names
        if data_source == 'ddsm_mass':
            columns = ['patient_id', 'breast_density', 'left or right breast', 'image view', 'subtlety']
            db_string = 'CREATE TABLE "DDSM_MASS" ' \
                        '("patient_id" varchar, ' \
                        '"breast_density" integer, ' \
                        '"left or right breast" varchar, ' \
                        '"image view" varchar, ' \
                        '"subtlety" integer);'
            insert_command = 'INSERT INTO DDSM_MASS VALUES (?, ?, ?, ?, ?)'

        if data_source == 'ddsm_calc':
            columns = ['patient_id', 'breast density', 'left or right breast', 'image view', 'subtlety']
            db_string = 'CREATE TABLE "DDSM_CALC" ' \
                        '("patient_id" varchar, ' \
                        '"breast_density" integer, ' \
                        '"left or right breast" varchar, ' \
                        '"image view" varchar, ' \
                        '"subtlety" integer);'
            insert_command = 'INSERT INTO DDSM_CALC VALUES (?, ?, ?, ?, ?)'
    else:
        raise NotImplementedError

    # read the csv file
    df = pd.read_csv(csv_file, sep=sep, engine='python', usecols=columns)  # data frame
    # print(df)
    df_as_list = df.values.tolist()
    # print(df_as_list[:3])

    # delete db file if exists
    if os.path.exists(db_path):
        os.remove(db_path)
        print('Previous database destroyed')

    con = sqlite3.Connection(db_path)
    cur = con.cursor()

    # create database
    cur.execute(db_string)
    print('Database created successfully')

    # insert items
    # for item in df_as_list:
    cur.executemany(insert_command, df_as_list)
    print('Inserted into database successfully')

    cur.close()
    con.commit()
    con.close()


# def create_db():
#     db_path = globals.params['db_path']
#
#     # delete db file if exists
#     if os.path.exists(db_path):
#         os.remove(db_path)
#         print('Previous database destroyed')
#
#     con = sqlite3.Connection(db_path)
#     cur = con.cursor()
#     cur.execute('CREATE TABLE "patients" '
#                 '("FileAnalyzed" varchar, "Manufacturer" varchar, "Laterality" varchar, "ViewPosition" varchar, '
#                 '"BreastArea_sqcm_" float, "DenseArea_sqcm_" float, "BreastDensity___" float, "basename" varchar, '
#                 '"source" varchar);')
#     print('Database created successfully')
#
#     combined, ks_rows, non_ks_rows = combine_csv_files(also_return_separately=True)
#     # for row in data:
#     #     if len(row) == 7:
#     #         row.append('')  # append empty string for the rows that do nat have the basename attribute
#
#     for row in ks_rows:
#         row.extend(['KS'])  # append data source
#
#     for row in non_ks_rows:
#         row.extend(['', 'nonKS'])  # append data source and empty string (they do not have basename)
#
#     for data in [ks_rows, non_ks_rows]:
#         cur.executemany('INSERT INTO patients VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', data)
#     print('Inserted into database successfully')
#
#     cur.close()
#     con.commit()
#     con.close()

def create_ddsm_query(mass_or_calc, left_or_right, view, attribute, value, limit=40):
    query_file = f'../data/ddsm/queries/{mass_or_calc}_{left_or_right}_{view}/{attribute}/{attribute}={value}.txt'
    with open(query_file) as f:
        lines = f.read().splitlines()

    subject_ids = [query_to_subject_id(mass_or_calc, patient_id, left_or_right, view) for patient_id in lines]
    subject_ids = subject_ids[:limit]
    query = ','.join(subject_ids)

    print(query)
    return query


def query_to_subject_id(mass_or_calc, patient_id, left_or_right, view):
    subject_id = f'{mass_or_calc}-Training_{patient_id}_{left_or_right}_{view}'
    return subject_id

