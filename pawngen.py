from io import StringIO
import argparse
from scipy import stats
import requests
import pandas as pd
import numpy as np
from urllib.parse import urlparse


def arg_parser():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument("--character", dest="character_name", default="Shadowbonobo",
                        help="Name of the relevant character")
    parser.add_argument("--file", dest="csvfile",
                        default="https://github.com/xskoak/reforges/raw/master/patchwerkreforge.csv",
                        help="Can be an a CSV file or a CSV URL.")
    parser.add_argument("--class", dest="character_class", default="Priest",
                        help="Class of the relevant character. Default is Priest")
    parser.add_argument("--spec", dest="spec", default="Shadow",
                        help="Specialization of the relevant character. Default is Shadow")
    parser.add_argument("--mainstat", dest="mainstat", default="intellect",
                        help="The primary stat of the relevant character. Default is intellect")
    args = parser.parse_args()


def data_parser(csv_path):
    parsed_input = urlparse(args.csvfile)
    if (parsed_input.scheme == 'http' or parsed_input.scheme == 'https'):
        csv_object = requests.get(args.csvfile).content.decode('utf-8')
    else:
        with open(args.csvfile, 'r') as content_file:
            csv_object = content_file.read()
    return csv_object


def re_load(csv_input):
    # If the first line is not removed pandas can't import due to BS header
    csv_object = csv_input
    csv_object = '\n'.join(csv_object.split('\n')[0:])
    # Regex operations to remove skew in the dataframe
    csv_object = csv_object.replace(' ', '')
    csv_object = csv_object.replace('DPS-Error', 'Error,')
    # Removes empty columns
    csv_object = pd.read_csv(StringIO(csv_object))
    csv_object = csv_object.dropna(axis=1, how='all')
    return csv_object


def regress_normalize(fixed_frame):
    slope_main, _, _, _, _ = stats.linregress(fixed_frame[args.mainstat], fixed_frame['DPS'])
    slope_crit, _, _, _, _ = stats.linregress(fixed_frame['crit_rating'], fixed_frame['DPS'])
    slope_haste, _, _, _, _ = stats.linregress(fixed_frame['haste_rating'], fixed_frame['DPS'])
    slope_mastery, _, _, _, _ = stats.linregress(fixed_frame['mastery_rating'], fixed_frame['DPS'])
    slope_versatility, _, _, _, _ = stats.linregress(fixed_frame['versatility_rating'], fixed_frame['DPS'])
    regression_list = [slope_main, slope_crit, slope_haste, slope_mastery, slope_versatility]
    norm_main = np.interp(slope_main, [min(regression_list), max(regression_list)], [1, 2])
    norm_crit = np.interp(slope_crit, [min(regression_list), max(regression_list)], [1, 2])
    norm_haste = np.interp(slope_haste, [min(regression_list), max(regression_list)], [1, 2])
    norm_mastery = np.interp(slope_mastery, [min(regression_list), max(regression_list)], [1, 2])
    norm_versatility = np.interp(slope_versatility, [min(regression_list), max(regression_list)], [1, 2])
    return norm_crit, norm_haste, norm_main, norm_mastery, norm_versatility


def print_pawn(norm_crit, norm_haste, norm_main, norm_mastery, norm_versatility):
        print("( Pawn: v1: \"{}\": Class={}, Spec={}, {}={}, CritRating={}, HasteRating={}, MasteryRating={}, Versatility={} )".format(
            args.character_name, args.character_class, args.spec, (args.mainstat).title(), norm_main, norm_crit,
            norm_haste, norm_mastery, norm_versatility))

if __name__ == '__main__':
    arg_parser()
    csv_object = data_parser(args.csvfile)
    csv_object = re_load(csv_object)
    norm_crit, norm_haste, norm_main, norm_mastery, norm_versatility = regress_normalize(csv_object)
    print_pawn(norm_crit, norm_haste, norm_main, norm_mastery, norm_versatility)