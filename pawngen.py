"""Tool to generate pawn string from a simc reforge file."""
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
                        help="Can be a CSV file path or a CSV URL.")
    parser.add_argument("--class", dest="character_class", default="Priest",
                        help="Class of the relevant character. Default is Priest")
    parser.add_argument("--spec", dest="spec", default="Shadow",
                        help="Specialization of the relevant character. Default is Shadow")
    parser.add_argument("--mainstat", dest="mainstat", default="intellect",
                        help="The primary stat of the relevant character. Default is intellect")
    args = parser.parse_args()


class DataList():
    def __init__(self, csv_path):
        # Read data to string
        parsed_input = urlparse(csv_path)
        if parsed_input.scheme == 'http' or parsed_input.scheme == 'https':
            self.csv_string = requests.get(args.csvfile).content.decode('utf-8')
        else:
            with open(args.csvfile, 'r') as content_file:
                self.csv_string = content_file.read()

    def regex(self):
        # If the first line is not removed pandas can't import due to BS header
        self.csv_string = '\n'.join(self.csv_string.split('\n')[1:])
        # Regex operations to remove skew in the dataframe
        self.csv_string = self.csv_string.replace(' ', '')
        self.csv_string = self.csv_string.replace('DPS-Error', 'Error,')

    def load_frame(self):
        self.data_frame = pd.read_csv(StringIO(self.csv_string))

    def drop_nan(self):
        self.data_frame = self.data_frame.dropna(axis=1, how='all')

    def regress(self):
        self.slope_main, _, _, _, _ = stats.linregress(self.data_frame[args.mainstat], self.data_frame['DPS'])
        self.slope_crit, _, _, _, _ = stats.linregress(self.data_frame['crit_rating'], self.data_frame['DPS'])
        self.slope_haste, _, _, _, _ = stats.linregress(self.data_frame['haste_rating'], self.data_frame['DPS'])
        self.slope_mastery, _, _, _, _ = stats.linregress(self.data_frame['mastery_rating'], self.data_frame['DPS'])
        self.slope_versatility, _, _, _, _ = stats.linregress(self.data_frame['versatility_rating'],
                                                              self.data_frame['DPS'])
        self.regression_list = [self.slope_main, self.slope_crit, self.slope_haste, self.slope_mastery,
                                self.slope_versatility]

    def normalize(self):
        self.norm_main = np.interp(self.slope_main, [min(self.regression_list), max(self.regression_list)], [1, 2])
        self.norm_crit = np.interp(self.slope_crit, [min(self.regression_list), max(self.regression_list)], [1, 2])
        self.norm_haste = np.interp(self.slope_haste, [min(self.regression_list), max(self.regression_list)], [1, 2])
        self.norm_mastery = np.interp(self.slope_mastery, [min(self.regression_list), max(self.regression_list)],
                                      [1, 2])
        self.norm_versatility = np.interp(self.slope_versatility,
                                          [min(self.regression_list), max(self.regression_list)], [1, 2])

    def print_pawn(self):
        print(
            "( Pawn: v1: \"{}\": Class={}, Spec={}, {}={}, CritRating={},"
            " HasteRating={}, MasteryRating={}, Versatility={} )".format(
                args.character_name, args.character_class, args.spec, args.mainstat.title(), self.norm_main,
                self.norm_crit,
                self.norm_haste, self.norm_mastery, self.norm_versatility))


if __name__ == '__main__':
    arg_parser()
    data_list = DataList(args.csvfile)
    data_list.regex()
    data_list.load_frame()
    data_list.drop_nan()
    data_list.regress()
    data_list.normalize()
    data_list.print_pawn()
