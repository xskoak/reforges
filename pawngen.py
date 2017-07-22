from io import StringIO
import argparse
from scipy import stats
import requests
import pandas as pd
import numpy as np

parser = argparse.ArgumentParser()
parser.add_argument("--character", dest="character_name", default="Shadowbonobo", help="Name of the relevant character")
parser.add_argument("--url", dest="url", default="https://github.com/xskoak/reforges/raw/master/patchwerkreforge.csv", help="URL of reforge csv. Default is https://github.com/xskoak/reforges/raw/master/patchwerkreforge.csv")
parser.add_argument("--class", dest="character_class", default="Priest", help="Class of the relevant character. Default is Priest")
parser.add_argument("--spec", dest="spec", default="Shadow", help="Specialization of the relevant character. Default is Shadow")
parser.add_argument("--mainstat", dest="mainstat", default="intellect", help="The primary stat of the relevant character. Default is intellect")

args = parser.parse_args()

csv_object = (requests.get(args.url).content).decode('utf-8')

#If the first line is not removed pandas can't import due to BS header
df = '\n'.join(csv_object.split('\n')[0:]) 
#Regex operations to remove skew in the dataframe
df = df.replace(' ', '')
df = df.replace('DPS-Error', 'Error,')

df = pd.read_csv(StringIO(df))
#Removes empty columns
df = df.dropna(axis=1,how='all')

slope_main,_,_,_,_ = stats.linregress(df[args.mainstat], df['DPS'])
slope_crit,_,_,_,_ = stats.linregress(df['crit_rating'], df['DPS'])
slope_haste,_,_,_,_ = stats.linregress(df['haste_rating'], df['DPS'])
slope_mastery,_,_,_,_ = stats.linregress(df['mastery_rating'], df['DPS'])
slope_versatility,_,_,_,_ = stats.linregress(df['versatility_rating'], df['DPS'])

regression_list = [slope_main, slope_crit, slope_haste, slope_mastery, slope_versatility]

norm_main = np.interp(slope_main,[min(regression_list), max(regression_list)], [1,2])
norm_crit = np.interp(slope_crit,[min(regression_list), max(regression_list)], [1,2])
norm_haste = np.interp(slope_haste,[min(regression_list), max(regression_list)], [1,2])
norm_mastery = np.interp(slope_mastery,[min(regression_list), max(regression_list)], [1,2])
norm_versatility = np.interp(slope_versatility,[min(regression_list), max(regression_list)], [1,2])

print("( Pawn: v1: \"{}\": Class={}, Spec={}, {}={}, CritRating={}, HasteRating={}, MasteryRating={}, Versatility={} )".format(args.character_name, args.character_class, args.spec, (args.mainstat).title(), norm_main, norm_crit, norm_haste, norm_mastery, norm_versatility))

