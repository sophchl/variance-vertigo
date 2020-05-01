# -*- coding: utf-8 -*-
"""
Created on Fri May  1 17:18:15 2020

@author: Sophia

input: spy 5min data (from processed)
output: RV upside and downside, daily frequency (to processed)

"""

#%% load dependencies

import os
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import statsmodels.stats as sms

#%% set parameters

start_date_paper = '1996-09-30'
end_date_paper = '2015-03-31'
end_date_crisis = '2007-12-31'

tradingdays_month = 21
h_month = [1,2,3,6,9,12]
k_month = [1,2,3,6,9,12]
k_days = k_month*tradingdays_month

#%% functions needed

def check_for_nans(data):
    # does nan check
    rows_w_nans = data[data.isnull().any(axis = 1)]
    number_nans = len(rows_w_nans)
    print('total number of rwos is:', len(data), '\n number of nans is:', number_nans, ' \n rows with nans are: \n', rows_w_nans)

#%% load data

names_dataframes = ['h01', 'h02', 'h03', 'h06', 'h09', 'h12']
data_directory_vrp = "data/processed/vrp/"
list_vrp_data = []

for file in os.listdir(data_directory_vrp):
    filename = data_directory_vrp + file
    df = pd.read_csv(filename, index_col = 0)
    df.index = pd.to_datetime(df.index)
    df.index.name = "date"
    list_vrp_data.append(df)
    
names_dataframes = ['k01', 'k02', 'k03', 'k06', 'k09', 'k12']
data_directory_return = "data/processed/excessreturn/"
list_return_data = []

for file in os.listdir(data_directory_return):
    if file.startswith('k'):
        filename = data_directory_return + file
        df = pd.read_csv(filename, index_col = 0)
        df.index = pd.to_datetime(df.index)
        list_return_data.append(df)
        continue
    else:
        continue

ex_return = pd.read_csv("data/processed/excessreturn/excessreturn_daily.csv", index_col = 0)

#%% one-variable regressions


for k in range(0,len(k_month)):
    
    # select the regressand
    yk1_data = list_return_data[k]
    
    for h in range(0,len(h_month)):
        
        # select the regressor
        xh1_data = list_vrp_data[h][['vrpu', 'vrpd']]
         
        # create the regression dataset
        data = pd.merge(xh1_data, yk1_data, on = 'date') 
        check_for_nans(data)
         
        # estimate a model vor vrpu and vrpd each
        model_1 = smf.ols('rtrn ~ vrpu', data = data, missing = 'drop').fit(cov_type='HAC', cov_kwds={'maxlags':1})
        model_2 = smf.ols('rtrn ~ vrpd', data = data, missing = 'drop').fit(cov_type='HAC', cov_kwds={'maxlags':1})

        # print results (can also be ommitted)
        print(model_1.summary())
        print(model_2.summary())

        # create a latex output and save it to file
        latex_output_1 = model_1.summary().as_latex()
        latex_output_2 = model_2.summary().as_latex()

        filename = "reg" + "k" + str(k_month[k]) + "h" + str(h_month[h]) 
        
        file_1 = open("results/regression/" + filename + "vrp_u.tex", 'a')
        file_1.write(latex_output_1)
        file_1.close()

        file_2 = open("results/regression/" + filename + "vrp_d.tex", 'a')
        file_2.write(latex_output_2)
        file_2.close()



