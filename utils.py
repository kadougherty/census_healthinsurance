#!/usr/bin/env python
# coding: utf-8

import requests
import time
import pandas as pd

def getCodeDictionary():
    host     = 'https://api.census.gov/data'
    year     =  2019
    dataset  = 'acs/acs1/pums/variables'
    base_url = "/".join([host, str(year), dataset]) 
    r        = requests.get(base_url)
    rlists   = r.json()
    code     = [item[0] for item in rlists if item[0].isupper()] #code in API
    label    = [item[1].lower() for item in rlists if item[0].isupper()] # description for each code

    codedict = {} # redudant with code, label but may make life easier later on
    count    = 0
    for lab in label:
        codedict[code[count]] = lab
        count += 1
    return codedict

def getVars():
    host     = 'https://api.census.gov/data'
    dataset  = 'acs/acs1/pums'
    year     = 2019
    return host, dataset, year

def variableDetails(codename):
    host     = 'https://api.census.gov/data'
    dataset  = 'acs/acs1/pums/variables'
    year     = 2019
    base_url = "/".join([host, str(year), dataset, codename + '.json']) 
    r        = requests.get(base_url)
    detail   = r.json()
    return detail

# function to get data from Census API, Public Access MicroData Samples using list of codes (max 50), state id number 
def callCensusApi(API_KEY,select_codes,stateid):
    query    = '?get='
    variable = ','.join(select_codes)
    base_url = "/".join([host, str(year), dataset]) + query + variable + '&for=state:' + stateid + '&key=' + API_KEY
    callbeg  = time.time()
    r        = requests.get(base_url) 
    colnames = variable.split(',')
    colnames.append('state')
    df       = pd.DataFrame(columns=colnames, data=r.json()[1:]) 
    tElapsed = time.time()-callbeg
    return (tElapsed,df)

# get full dataframe (all variables in code) for one state. uses callCensusAPI function above
def getCensusDataByState(state_id):
    max_var_call = 50
    start_var_n  = 0
    end_var_n = start_var_n + max_var_call
    totalTime = 0
    while end_var_n <= len(code): 
        tElapsed, hdf = callCensusApi(API_KEY,code[start_var_n:end_var_n],state_id)
        if start_var_n == 0:
            df = hdf.sample(nsamples)
            rowid = df.index
            df = df.reset_index()
        else:
            sub = hdf.iloc[rowid]
            sub = sub.reset_index()
            df = pd.merge(df,sub,how='left',on='index')
            del sub
        totalTime = totalTime + tElapsed
        start_var_n = end_var_n + 1
        end_var_n = start_var_n + max_var_call
    if df.shape[1] < len(code):
        tElapsed, hdf = callCensusApi(API_KEY,code[start_var_n:len(code)],state_id)
        sub = hdf.iloc[rowid]
        sub = sub.reset_index()
        df  = pd.merge(df,sub,how='left',on='index')      
        totalTime = totalTime + tElapsed
        del hdf
    return (df,totalTime)
    
    