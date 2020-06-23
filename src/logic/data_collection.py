import csv
import matplotlib.pyplot as plt

import globals


def read_csv_file(filename):
    # lines = []
    with open(filename) as f:
        reader = csv.reader(f, delimiter=';')
        lines = [row for row in reader]
    return lines


def density_hist(densities, view):
    plt.clf()
    count_or_prob = 'Count'
    # view = 'MLO' if 'MLO' in save_to else 'CC'

    # print(f'denisty min: {min(densities)} - max: {max(densities)}')
    # input()
    logscale = True

    plt.hist(densities, density=count_or_prob == 'Probability', bins=100)  # `density=False` would make counts

    if logscale:
        plt.xscale('log')

    plt.xlabel(f'{view} Log Density percent' if logscale else f'{view} Density percent')
    plt.ylabel(count_or_prob)

    # if save_to:
    save_to = f'../tmp/figs/{view} {"log" if logscale else "linear"}.jpg'
    plt.savefig(save_to)

    # if not no_show:
    #    plt.show()


def read_attribute_from_csv(attribute):
    filename = globals.params['csv_file']
    rows = read_csv_file(filename)

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
    index = attributes.index(attribute)
    values = [row[index] for row in rows[1:]]
    return values


def read_breast_densities(view=None, limit_to=None, plot=True):
    filename = globals.params['csv_file']
    rows = read_csv_file(filename)
    # save_to = None  # do not save the histogram fig by default
    # print('len:', len(rows))  # len: 329,450 (the first line being attributes)
    # for i, item in enumerate(rows[0]):
    #     print(f'{i}: {item}\n')

    if view:  # consider only images with this view
        rows = [row for row in rows if row[3] == view]
        # save_to = f'../tmp/figs/{view}.jpg'
        print(f'only considering rows with view: {view}')

    print(f'len rows: {len(rows):,}')
    densities = [float(row[6]) for row in rows[1:]]  # exclude the first rwo which is the attributes
    # print(f'len densities: {len(densities):,}')

    if limit_to:
        densities = densities[:limit_to]

    if plot:
        density_hist(densities, view)

