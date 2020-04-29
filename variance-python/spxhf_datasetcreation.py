# -*- coding: utf-8 -*-
"""
Created on Sat Apr  4 11:32:13 2020

@author: Sophia

input: multiple csv files of hf spy data (from raw)
output: one csv files with 5-min spx data (to raw and processed)

description:
This code loops over the single files that contain the spy high-frequency data
and creates one dataset to approximate spx.
Several files are saved into the "data/raw" files on the way to have multiple
points where the code can be started from. The final version is saved both 
to the "data/raw" and the "data/processeed" directory.

"""

#%% setup

import numpy as np
import pandas as pd
import datetime as dt
import pandas_market_calendars as mcal

#%% functions needed

def separate_tradingday_overnight(data):
    day = data[(data.index.time >= dt.time(9,30,0)) & 
               (data.index.time <= dt.time(16,0,0))]
    nightindex = data.index.difference(day.index)
    night = data.loc[nightindex,]
    return(day, night)



#%% loop over all files in directory to import the data from manual download
# commented out because code runs long and I saved an intermediate result afterwards so don't run if not necessary

'''
# directly aggregate to mide price in 5min during trading day

# this section takes quite long!

data_directory = "data/raw/spxhf3"

list_dataframes = []

for file in os.listdir(data_directory):
    if file.endswith('.csv'):
        filename = data_directory + "/" + file
        df = pd.read_csv(filename, )
        df.index = pd.to_datetime(df['DATE'].astype(str) + ":" + df['TIME'], format = '%Y%m%d:%H:%M:%S')
        df['mid'] = (df['BID'] + df['OFR'])/2
        df = df.drop(['BID', 'OFR', 'DATE', 'TIME', 'SYMBOL'], axis = 1)
        df = df.resample('5T').median()
        df = separate_tradingday_overnight(df)[0]
        list_dataframes.append(df)
        print(file)
        continue
    else:
        continue
    
#%% create one big dataframe and safe it to be able to continue from here

spx1 = pd.concat(list_dataframes)
spx1 = spx1.sort_index()

spx1.to_csv("data/raw/spxhf4/5minspx2007.csv")
'''

#%% import data from 2007

spx1 = pd.read_csv("data/raw/spxhf4/5minspx2007.csv", index_col = 0)
spx1.index = pd.to_datetime(spx1.index)
 
#%% import the data 2008 - 2020

spx2_raw = pd.read_csv("data/raw/spxhf2/SPY/SPY.csv", index_col = 0)
spx2_raw.index = pd.to_datetime(spx2_raw.index)
spx2_raw['date'] = spx2_raw.index.date
spx2_raw['time'] = spx2_raw.index.time
spx2_raw['mid'] = (spx2_raw.open + spx2_raw.close)/2

spx2_raw[spx2_raw.isnull().any(axis = 1)]

spx5 = spx2_raw.resample('5T').median()
spx5 = separate_tradingday_overnight(spx5)[0]
spx5 = spx5.drop(['open', 'close'], axis = 1)

spx5[spx5.isnull().any(axis = 1)]


#%% join data 2007 - 2020 and save them

spx1 = spx1[spx1.index.year < 2008]
spx = pd.concat([spx1, spx5])

print('Are there overlaps?', True in spx.index.duplicated(keep = "first"))

spx.to_csv("data/raw/spxhf4/5minspx20072.csv")

#%% import dataset 2007 - 2020

spx = pd.read_csv("data/raw/spxhf4/5minspx20072.csv", index_col = 0)
spx.index = pd.to_datetime(spx.index)

#%% add original dates for Nan detection

spx2_raw = pd.read_csv("data/raw/spxhf2/SPY/SPY.csv", index_col = 0)
spx2_raw.index = pd.to_datetime(spx2_raw.index)
spx1 = pd.read_csv("data/raw/spxhf4/5minspx2007.csv", index_col = 0)
spx1.index = pd.to_datetime(spx1.index)

available_dates = pd.concat([pd.DataFrame(np.unique(spx1.index.date)), 
                             pd.DataFrame(np.unique(spx2_raw.index.date))])
available_dates.columns = ['date']

spx['date'] = spx.index.date

#%% check for missing values (remove holiday and weekend)

# look at initial dataset
missing_days = pd.date_range(start = dt.date(2008,1,2), end = dt.date(2020,4,9)).difference(spx.index.date)
print('length of dataset initial:', len(spx))
print('number of missing days compared to all dates 2.1.2008 - 9.4.2020:', len(missing_days))
print('number of Nans:', spx.isnull().sum())
print('number of days in dataset', len(np.unique(spx['date'])))

# remove weekends 
spx = spx[spx.index.dayofweek < 5]
print('length of dataset without weekend:', len(spx))
print('number of Nans:', spx.isnull().sum())
print('number of days in dataset', len(np.unique(spx['date'])))

# remove non-trading days
nyse = mcal.get_calendar('NYSE')
early = nyse.schedule(start_date=spx.index.date[1], end_date=spx.index.date[-1])
no_trading_days = np.setdiff1d(list(spx.index.date),list(early.index.date))

spx['to_drop'] = [1 if x in no_trading_days else 0 for x in spx.index.date]
index_to_drop = spx[spx['to_drop'] == 1].index
spx = spx.drop(index = index_to_drop, columns = ['to_drop'])

print('length of dataset without holiday days:', len(spx))
print('number of Nans:', spx.isnull().sum())
print('number of days in dataset', len(np.unique(spx['date'])))

# look what Nans we have left
spx.isnull().values.any()
spx[spx.isna().any(axis=1)]

# remove days that were not in original sample (probably non-trading days, too)
spx = spx[spx['date'].isin(available_dates['date'])]
                                 
print('length of dataset without days that were not in sample before:', len(spx))
print('number of Nans:', spx.isnull().sum())
print('number of days in dataset', len(np.unique(spx['date'])))

#%% save this version (2007 - 2020, no days with all Nan but some intraday Nan)

spx.to_csv("data/raw/spxhf4/5minspx20073.csv")

#%% check for zeros (2 rows)

spx = spx.replace(0, np.nan)
spx[spx.mid.eq(0)]

#%% which dates still have Nans?

rows_w_nan = spx[spx.isnull().any(axis = 1)]
days_w_nan = np.unique(rows_w_nan.index.date)
print('number of days with Nans:', len(days_w_nan))

# how many nans per date?
list_nan_per_day = []
for i in range(1,len(np.unique(rows_w_nan.index.date))):
    count = len(rows_w_nan[rows_w_nan.index.date == days_w_nan[i]])
    list_nan_per_day.append(count)
    
print('Nans per day that has Nans:', list_nan_per_day)


#%% interpolate missing 5-min values (91)

spx['mid'] = spx['mid'].interpolate()

rows_w_nan = spx[spx.isnull().any(axis = 1)]
days_w_nan = np.unique(rows_w_nan.index.date)
print('number of Nans:', len(days_w_nan))


#%% save this version (2007 - 2020, no Nan)

spx.to_csv("data/raw/spxhf4/5minspx20074.csv")
spx.to_csv("data/processed/spxhf/spx5min.csv")

#%% sorted temporal checks

'''
# temporal check: time frame we have for option data
start = dt.date(2007,1,3)
end = dt.date(2015,10,7)
spx = spx[(spx.date >= start) & (spx.date < end)]

rows_remove_c = spx[~spx['date'].isin(available_dates['date'])]
np.unique(rows_remove_c['date'])
'''
    


