# -*- coding: utf-8 -*-
"""
Created on Fri May  1 17:18:15 2020

@author: Sophia

input: vrp and excess returns (from processed)
output: in-sample regression results (to results)

"""

#%% load dependencies

import os
import pandas as pd
import statsmodels.formula.api as smf
import pandas_market_calendars as mcal

#%% set parameters

start_date_paper = '1996-09-30'
end_date_paper = '2015-03-31'
end_date_crisis = '2007-12-31'

tradingdays_month = 21
h_month = [1,2,3,6,9,12]
k_month = [1,2,3,6,9,12]
k_days = k_month*tradingdays_month

# trading days in our period of interest
nyse = mcal.get_calendar('NYSE')

#%% functions needed

def check_for_nans(data):
    # does nan check
    rows_w_nans = data[data.isnull().any(axis = 1)]
    number_nans = len(rows_w_nans)
    print('total number of rows is:', len(data), '\n number of nans is:', number_nans)
    

def model_list_to_latex1(list_models):
    # this function creates a latex code for our models in one variable
    # the loop is in such a strange way (divide by 6, but take i+..) because we want 
    # one line per k, and every 6 values k increases by one
    # list_models includes model_kh as model_11, model12, model13.., model21, model22,...
    
    list_of_lines = []
    list_month_repeat = [1,1,1,1,1,1,2,2,2,2,2,2,3,3,3,3,3,3,6,6,6,6,6,6,9,9,9,9,9,9,12,12,12,12,12,12]
    
    for i in [0,6,12,18,24,30]:
        my_line = (str(list_month_repeat[i]) + " & " + 
                   str(list_models[i].pvalues[1].round(3)) + " & " +
                   str(list_models[i].rsquared_adj.round(3)) + " & " +
                   str(list_models[i+1].pvalues[1].round(3)) + " & " +
                   str(list_models[i+1].rsquared_adj.round(3)) + " & " +
                   str(list_models[i+2].pvalues[1].round(3)) + " & " +
                   str(list_models[i+2].rsquared_adj.round(3)) + " & " +
                   str(list_models[i+3].pvalues[1].round(3)) + " & " +
                   str(list_models[i+3].rsquared_adj.round(3)) + " & " +
                   str(list_models[i+4].pvalues[1].round(3)) + " & " + 
                   str(list_models[i+4].rsquared_adj.round(3)) + " & " +
                   str(list_models[i+5].pvalues[1].round(3)) + " & " + 
                   str(list_models[i+5].rsquared_adj.round(3)) + " \\\[6pt]")
        
        list_of_lines.append(my_line)
        list_of_lines.append("\n")

    panel = "".join(list_of_lines)
    return(panel)


def model_list_to_latex2(list_models):
    # this function creates a latex code for our models in two variables
    # see model_list_to_latex1
    
    list_of_lines = []
    list_month_repeat = [1,1,1,1,1,1,2,2,2,2,2,2,3,3,3,3,3,3,6,6,6,6,6,6,9,9,9,9,9,9,12,12,12,12,12,12]
    
    for i in [0,6,12,18,24,30]:
        my_line = (str(list_month_repeat[i]) + " & " + 
                   str(list_models[i].pvalues[1].round(3)) + " & " +
                   str(list_models[i].pvalues[2].round(3)) + " & " +
                   str(list_models[i].rsquared_adj.round(3)) + " & " +
                   str(list_models[i+1].pvalues[1].round(3)) + " & " +
                   str(list_models[i+1].pvalues[2].round(3)) + " & " +
                   str(list_models[i+1].rsquared_adj.round(3)) + " & " +
                   str(list_models[i+2].pvalues[1].round(3)) + " & " +
                   str(list_models[i+2].pvalues[2].round(3)) + " & " +
                   str(list_models[i+2].rsquared_adj.round(3)) + " & " +
                   str(list_models[i+3].pvalues[1].round(3)) + " & " +
                   str(list_models[i+3].pvalues[2].round(3)) + " & " +
                   str(list_models[i+3].rsquared_adj.round(3)) + " & " +
                   str(list_models[i+4].pvalues[1].round(3)) + " & " + 
                   str(list_models[i+4].pvalues[2].round(3)) + " & " + 
                   str(list_models[i+4].rsquared_adj.round(3)) + " & " +
                   str(list_models[i+5].pvalues[1].round(3)) + " & " + 
                   str(list_models[i+5].pvalues[2].round(3)) + " & " + 
                   str(list_models[i+5].rsquared_adj.round(3)) + " \\\[6pt]")
        
        list_of_lines.append(my_line)
        list_of_lines.append("\n")

    panel = "".join(list_of_lines)
    return(panel)



#%% load data

names_dataframes = ['h01', 'h02', 'h03', 'h06', 'h09', 'h12']
data_directory_vrp = "data/processed/vrp/"
list_vrp_data = []

for file in os.listdir(data_directory_vrp):
    filename = data_directory_vrp + file
    df = pd.read_csv(filename, index_col = 0)
    df.index = pd.to_datetime(df.index)
    df.index.name = "date"
    df['skw'] = df.vrpu - df.vrpd
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

#%% one-variable regressions

list_models_upside = []
list_models_downside = []
list_models_total = []
list_models_skw = []

for k in range(0,len(k_month)):
    
    # select the regressand
    yk1_data = list_return_data[k]
    
    for h in range(0,len(h_month)):
        
        # select the regressor
        xh1_data = list_vrp_data[h][['vrpu', 'vrpd', 'vrp', 'skw']]
         
        # create the regression dataset
        
        data = pd.merge(xh1_data, yk1_data, on = 'date') 
        
        '''
                
        # do nan and day check
        
        start = max(yk1_data.index[0], xh1_data.index[0])
        end = min(yk1_data.index[-1], xh1_data.index[-1])
        early = nyse.schedule(start_date = start, end_date = end)
        
        yk1_data2 = yk1_data[(yk1_data.index >= start) & (yk1_data.index <= end)]
        xh1_data2 = xh1_data[(xh1_data.index >= start) & (xh1_data.index <= end)]
        
        print('yk1 ranges from', yk1_data.index[0], 'to', yk1_data.index[-1], 'number of days is:', len(yk1_data.index), '.\n',
              'xh1 ranges from', xh1_data.index[0], 'to', xh1_data.index[-1], 'number of days is:', len(xh1_data.index), '.\n',
              'their common date range is', start, 'to', end, 'number of trading days in that range is:', len(early.index), '.\n',
              'yk1 in common range has days:', len(yk1_data2.index), 
              'xh1 in common range has days:', len(xh1_data2.index),                  
              'the merged dataframes ranges from:', data.index[0], 'to', data.index[-1], 'number of days is:', len(data.index), '.')
        
        print(xh1_data.index[~xh1_data.index.isin(yk1_data.index)])
        print(yk1_data.index[~yk1_data.index.isin(xh1_data.index)])
        
        check_for_nans(yk1_data)
        check_for_nans(xh1_data)
        check_for_nans(data)
        
        '''
        
        # estimate a model for vrp, vrpu and vrpd each
        model_1 = smf.ols('rtrn ~ vrpu', data = data, missing = 'drop').fit(cov_type='HAC', cov_kwds={'maxlags':1})
        model_2 = smf.ols('rtrn ~ vrpd', data = data, missing = 'drop').fit(cov_type='HAC', cov_kwds={'maxlags':1})
        model_3 = smf.ols('rtrn ~ vrp', data = data, missing = 'drop').fit(cov_type='HAC', cov_kwds={'maxlags':1})
        model_4 = smf.ols('rtrn ~ skw', data = data, missing = 'drop').fit(cov_type='HAC', cov_kwds={'maxlags':1})
        
        # create a latex output and save it to file
        latex_output_1 = model_1.summary().as_latex()
        latex_output_2 = model_2.summary().as_latex()
        latex_output_3 = model_3.summary().as_latex()
        latex_output_4 = model_4.summary().as_latex()
        
        file_1 = open("results/regression/vrp_u.tex", 'a')
        file_1.write("regression model for VRPU, k = " + str(k_month[k]) + " h = " + str(h_month[h]))
        file_1.write(latex_output_1)
        file_1.write("\\\ \n\n")
        file_1.close()

        file_2 = open("results/regression/vrp_d.tex", 'a')
        file_2.write("regression model for VRPD, k = " + str(k_month[k]) + " h = " + str(h_month[h]))
        file_2.write(latex_output_2)
        file_2.write("\\\ \n\n")
        file_2.close()
        
        file_3 = open("results/regression/vrp.tex", 'a')
        file_3.write("regression model for VRP, k = " + str(k_month[k]) + " h = " + str(h_month[h]))
        file_3.write(latex_output_3)
        file_3.write("\\\ \n\n")
        file_3.close()
        
        file_4 = open("results/regression/skew.tex", 'a')
        file_4.write("regression model for skewness, k = " + str(k_month[k]) + " h = " + str(h_month[h]))
        file_4.write(latex_output_4)
        file_4.write("\\\ \n\n")
        file_4.close()
        
        # append the output to model list
        list_models_upside.append(model_1)
        list_models_downside.append(model_2)
        list_models_total.append(model_3)
        list_models_skw.append(model_4)


#%% add one-variable resgressions to latex

panelA = model_list_to_latex1(list_models_total)
panelB = model_list_to_latex1(list_models_downside)
panelC = model_list_to_latex1(list_models_upside)
panelD = model_list_to_latex1(list_models_skw)
 
file_3 = open("results/regression/regression_overview.tex", "a")
file_3.write(panelA)
file_3.write(panelB)
file_3.write(panelC)
file_3.write(panelD)
file_3.close()

#%% two variable regression

list_models_premium = []
list_models_iv = []
list_models_rv = []

for k in range(0,len(k_month)):
    
    # select the regressand
    yk1_data = list_return_data[k]
    
    for h in range(0,len(h_month)):
        
        # select the regressor
        xh1_data = list_vrp_data[h][['vrpu', 'vrpd', 'ivu', 'ivd', 'rvu', 'rvd']]
         
        # create the regression dataset
        
        data = pd.merge(xh1_data, yk1_data, on = 'date') 
                
        # estimate the model with both vrpu, vrpd
        model_1 = smf.ols('rtrn ~ vrpu + vrpd', data = data, missing = 'drop').fit(cov_type='HAC', cov_kwds={'maxlags':1})
        model_2 = smf.ols('rtrn ~ ivu + ivd', data = data, missing = 'drop').fit(cov_type='HAC', cov_kwds={'maxlags':1})
        model_3 = smf.ols('rtrn ~ rvu + rvd', data = data, missing = 'drop').fit(cov_type='HAC', cov_kwds={'maxlags':1})

        # create a latex output and save it to file
        latex_output_1 = model_1.summary().as_latex()
        latex_output_2 = model_2.summary().as_latex()
        latex_output_3 = model_3.summary().as_latex()
        
        file_1 = open("results/regression/vrp_both.tex", 'a')
        file_1.write("regression model for VRPU, k = " + str(k_month[k]) + " h = " + str(h_month[h]))
        file_1.write(latex_output_1)
        file_1.write("\\\ \n\n")
        file_1.close()

        file_2 = open("results/regression/iv_both.tex", 'a')
        file_2.write("regression model for VRPD, k = " + str(k_month[k]) + " h = " + str(h_month[h]))
        file_2.write(latex_output_2)
        file_2.write("\\\ \n\n")
        file_2.close()
        
        file_3 = open("results/regression/rv_both.tex", 'a')
        file_3.write("regression model for VRP, k = " + str(k_month[k]) + " h = " + str(h_month[h]))
        file_3.write(latex_output_3)
        file_3.write("\\\ \n\n")
        file_3.close()
        
        
        # append the output to model list
        list_models_premium.append(model_1)
        list_models_iv.append(model_2)
        list_models_rv.append(model_3)
        
#%% add two-variable regression to latex

panelA = model_list_to_latex2(list_models_premium) 
panelB = model_list_to_latex2(list_models_iv) 
panelC = model_list_to_latex2(list_models_rv) 

file_3 = open("results/regression/regression_overview.tex", "a")
file_3.write(panelA)
file_3.write(panelB)
file_3.write(panelC)
file_3.close() 

