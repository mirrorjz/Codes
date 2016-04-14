#!/usr/bin/env python
# -*- coding: utf-8 -*- 

#important note: 
#gloables will be created for each process. e.g. 2 processes = 3 copies of gloables
# for this program, I find that 2-3 processes will take all the momories

### Make prediction for each user:  
#   General strategy: 1) Predictions based on the history of detail (and maybe visit, later versions)
#                     2) Predictions based on the popularity of the coupon among large number of users 
#						 mainly for the users who have very small number of transactions in the history
#
#
#####

import meanPrecision
import pandas as pd
import numpy as np
from scipy.sparse import csr_matrix
from datetime import datetime
from math import exp
import math
from multiprocessing import Pool #, Process, Lock
import time
from datetime import timedelta
import gc # gabage collector



coupon_detail_train = pd.read_csv('coupon_detail_train.csv')

coupon_visit_train = pd.read_csv('coupon_visit_train.csv')

coupon_list_train  = pd.read_csv('coupon_list_train.csv')

coupon_list_test = pd.read_csv('coupon_list_test.csv')

user_list = pd.read_csv('user_list.csv')

coupon_list_test = pd.read_csv('coupon_list_test.csv')

coup_bought_usrcomb = pd.merge(user_list, coupon_detail_train, on = 'USER_ID_hash') 

# complete information for both user and coupon for a coupon bought
# Int64Index: 168996 entries, 0 to 168995
# Data columns (total 34 columns):
coup_usr_complete = pd.merge(coup_bought_usrcomb, coupon_list_train, on = 'COUPON_ID_hash', sort = False)

# top user and their bought coupon number
userID_purched_vcounts = coupon_detail_train['USER_ID_hash'].value_counts()

# Convert all dates to datetime format. 
uc_I_DATE = pd.to_datetime(coup_usr_complete['I_DATE'])
uc_REG_DATE = pd.to_datetime(coup_usr_complete['REG_DATE'])
uc_WITHDRAW_DATE = pd.to_datetime(coup_usr_complete['WITHDRAW_DATE'])
uc_DISPFROM = pd.to_datetime(coup_usr_complete['DISPFROM'])
uc_DISPEND = pd.to_datetime(coup_usr_complete['DISPEND'])
uc_VALIDFROM = pd.to_datetime(coup_usr_complete['VALIDFROM'])
uc_VALIDEND = pd.to_datetime(coup_usr_complete['VALIDEND'])

# A simple uc_complete info for further analysis (could be modified later on)
# Initially, age, item_count, coupon valid period and useable dates and large areas are 
# all ignored.
uc_simple = coup_usr_complete[['SEX_ID', 'SMALL_AREA_NAME', 'PREF_NAME', 'USER_ID_hash', 'COUPON_ID_hash', 'CAPSULE_TEXT','GENRE_NAME', 'PRICE_RATE', 'DISCOUNT_PRICE','ken_name', 'small_area_name']]
uc_simple_wdates = uc_simple.join(uc_I_DATE).join(uc_REG_DATE).join(uc_WITHDRAW_DATE).join(uc_DISPFROM).join(uc_DISPEND).join(uc_VALIDFROM).join(uc_VALIDEND)

def dictCat(df, cat_name):
    """
    Given the dataframe, produce a dictionary of this category, the key is the string, either
    'CAPSULE_TEXT', 'GENRE_NAME', 'small_area_name' or 'ken_name'. The values should be from 0 to the 
    total number of this category - 1
    
    parameters
    ----------
    df: the dataframe used. e.g. coupon_list_train
    cat_name: a category name
                 
    Returns
    -------
    A series of data, the index is the category names 
    """
    cats = df[cat_name].unique()
    dict = {}
    totalcats = len(cats)
    for i in range(totalcats):
        dict[cats[i]] = i
    result = pd.Series(dict)
    result.sort()
    return result
    
## total 13    
genreDict = dictCat(coupon_list_train, 'GENRE_NAME')
## total 25
capsuleDict = dictCat(coupon_list_train, 'CAPSULE_TEXT')
## total 55
smallareaDict = dictCat(coupon_list_train, 'small_area_name')
## total 47
kenNameDict = dictCat(coupon_list_train, 'ken_name')
## (prefName, total 48, as NaN is included, prefNameDict.index[0] = nan, math.isnan(prefNameDict.index[0]) = True)
prefNameDict = dictCat(user_list, 'PREF_NAME')

###
# The following code test if preName and kenName overlap
# x = prefNameDict.index[0]  
# prefNameDict_noNaN = prefNameDict.drop(x) 
# arr_pref = prefNameDict_noNaN.index
# arr_ken = kenNameDict.index
# set(arr_pref) == set(arr_ken)
# This is true.

# Make a dictionary (ks_dict) that links ken_name (keys) to small_area_name (a list of small areas)
locations = coupon_list_train.groupby(['ken_name','small_area_name']).size()
localink = locations.index
num = len(localink)
ks_dict = {}
for i in range(num):
    ken, small = localink[i]
    if ken in ks_dict:
        ks_dict[ken].append(small)
    else:
        ks_dict[ken] = []
        ks_dict[ken].append(small)


def userHistoryVec(df, cuttime, cat_name, tau):
    """
    Given a df for this user, create a vector (mainly composed of category and small area name) 
    according to his/her history. 
    
    parameters
    ----------
    user_ID: user_ID hash value (str)
    df: the dataframe for this user which is used to calculate the vector
    cat_name: either "GENRE_NAME" or "CAPSULE_TEXT"
    cuttime: the cutting time, in the test situation, it should be datetime(2012, 6, 24)
    tau: a float, the time constant for the exponential decay for the history
               
    Returns
    -------
    A sparse vector that  
    """
    df1 = df.drop_duplicates(['COUPON_ID_hash'])    # only unique coupons are being counted
    dict_cat = {}
    if cat_name == 'GENRE_NAME':
        dict_cat = genreDict
    else:
        dict_cat = capsuleDict
    catNum = len(dict_cat.keys())
    col_num = catNum * 55       ## 55 is the total names of small_area_name
    result = csr_matrix((1,col_num))          ## initialize an empty 1 * col_num sparse matrix 
    df_index = df1.index
    for x in df_index:
        catName = df1[cat_name][x]
        smallArea = df1.small_area_name[x]
        j = dict_cat[catName]
        i = smallareaDict[smallArea]
        date = df1.I_DATE[x]
        timespan = (cuttime - date).days   ## number of days past since the cuttime
        # print timespan
        data = np.array([1.0])
        col = np.array([i * catNum + j])
        row = np.array([0])
        mat = csr_matrix((data,(row,col)), shape=(1,col_num))
        result = result + exp(-timespan/tau) * mat
    return result
    
    
    
### Baseline vectors: 
## probability of each category for female and male: each of them are a Series data structure:
## the index is the category name and the value is the basic probability. The stats are from 
## users who only bought one coupon (it is fairly close to all stats) since it is mainly used to 
## help predict the purchase of rare buyers who have little history.

## Rank of users that bought the coupons
user_purch_rank = coupon_detail_train['USER_ID_hash'].value_counts()
## make this series to a datafram
data = {'USER_ID_hash': user_purch_rank.index, 'bought_num': user_purch_rank.values}
user_purch_rank_df = pd.DataFrame(data)
user_purch_rank_complete = pd.merge(user_purch_rank_df, coup_usr_complete, on = 'USER_ID_hash', sort = False) 
## Users who only bought one coupon
miniBuyers = user_purch_rank_complete[user_purch_rank_complete.bought_num == 1]
## for category is 'GENRE_NAME':
total_f =  miniBuyers.groupby('SEX_ID').size()['f']
total_m = miniBuyers.groupby('SEX_ID').size()['m']
baseNum_f_g = miniBuyers[miniBuyers.SEX_ID == 'f'].groupby(['GENRE_NAME']).size()
baseProb_f_g = baseNum_f_g/(float(total_f))
baseNum_m_g = miniBuyers[miniBuyers.SEX_ID == 'm'].groupby(['GENRE_NAME']).size()
baseProb_m_g = baseNum_m_g/(float(total_m))
baseProb_m_g['ビューティー'] = 0

## for category is 'CAPSULE_TEXT':
baseNum_f_cap = miniBuyers[miniBuyers.SEX_ID == 'f'].groupby(['CAPSULE_TEXT']).size()
baseProb_f_cap = baseNum_f_cap/(float(total_f))
baseNum_m_cap = miniBuyers[miniBuyers.SEX_ID == 'm'].groupby(['CAPSULE_TEXT']).size()
baseProb_m_cap = baseNum_m_cap/(float(total_m))

## Determine the baseline sparse matrix for these categories:
## '宅配', 'その他のクーポン', 'ホテル・旅館', 'ギフトカード', the relative percentage of all coupons bought are 
## used to determine the number for each location. (This is a very rough estimation).

def cat_base(df, cat_name, category):
    """
    For a certain category name, produce a series that contains the percentage of coupons bought 
    for each small_area.
    
    General strategy:  
    
    parameters
    ----------
    df: the dataframe used
    cat_name: either "GENRE_NAME" or "CAPSULE_TEXT" 
         
    Returns
    -------
    a sparse vector
    """
    dict_cat = {}
    if cat_name == 'GENRE_NAME':
        dict_cat = genreDict
    else:
        dict_cat = capsuleDict
    catNum = len(dict_cat.keys())
    col_num = catNum * 55   
    base_num = df[df[cat_name] == category].groupby('small_area_name').size()      # number of coupon in this category for a specific location
    total_num = len(df[df[cat_name] == category])
    base_distr = base_num/(float(total_num))
    length = len(base_distr)           # The non-zero number of the sparse matrix
    row = np.zeros(length) 
    colList = []
    for i in range(length):
        c_index = smallareaDict[base_distr.index[i]] * catNum +  dict_cat[category]
        colList.append(c_index) 
    col = np.array(colList)
    result = csr_matrix((base_distr.values,(row,col)), shape=(1,col_num)) 
    return result

delivery_base_g = cat_base(uc_simple, 'GENRE_NAME','宅配')  
other_base_g = cat_base(uc_simple, 'GENRE_NAME','その他のクーポン')
hotel_base_g = cat_base(uc_simple, 'GENRE_NAME','ホテル・旅館')
giftcard_base_g = cat_base(uc_simple, 'GENRE_NAME','ギフトカード') 
# base_g = delivery_base_g + other_base_g + hotel_base_g + giftcard_base_g

"""
Test code 
showSparsemat(delivery_base_g)
showSparsemat(other_base_g)
showSparsemat(hotel_base_g)
showSparsemat(giftcard_base_g)

""" 
# The variable baselines and the location correlation            
cat_var = np.array(['エステ', 'グルメ', 'ネイル・アイ', 'ヘアサロン', 'リラクゼーション', 'レジャー', 'レッスン', '健康・医療'])
cat_var_prob = np.array([0.66, 0.63, 0.68, 0.74, 0.66, 0.48, 0.39, 0.60]) 
cat_var_prob_sm = np.array([0.88, 0.89, 0.89, 0.90, 0.90, 0.48, 0.49, 0.81])

def baseVec(df, cat_name):
    """
    Given a user, create a vector (mainly composed of category and small area name) according to basic information
    of the user (mainly PREF name, SEX_ID, initially). If no PREF info is available, then SMALL_AREA_NAME will be 
    used.
    
    General strategy: For the categories that have low correlation with the user's location, the values are largely calculated above
    For the categories have a relatively high correlation with the user's location, pref_name is used. Otherwise, if the pref_name is 
    naN, then the "SMALL_AREA_NAME" list are used. 
    
    parameters
    ----------
    df: the dataframe for this user which is used to calculate the vector
    cat_name: either "GENRE_NAME" or "CAPSULE_TEXT"       
    Returns
    -------
    a sparse vector
    """
    sex = df.SEX_ID[df.index[0]]
    if sex == 'f':
        if cat_name == 'GENRE_NAME':
            baseProb_seri = baseProb_f_g       # baseline probability for female 
        else: 
            baseProb_seri = baseProb_f_cap
    else:
        if cat_name == 'GENRE_NAME':
            baseProb_seri = baseProb_m_g
        else: 
            baseProb_seri = baseProb_m_cap      # baseline probability for male
    dict_cat = {}
    if cat_name == 'GENRE_NAME':
        dict_cat = genreDict
    else:
        dict_cat = capsuleDict
    catNum = len(dict_cat.keys())
    col_num = catNum * 55 
    result = csr_matrix((1,col_num))  
    user_pfname = df.PREF_NAME[df.index[0]]
    if ((type(user_pfname) != str) and math.isnan(user_pfname)): 
        small_areas = df.SMALL_AREA_NAME.unique()
        var_prob = cat_var_prob_sm
    else:
        small_areas = np.array(ks_dict[user_pfname])
        var_prob = cat_var_prob
    sm_num = len(small_areas) 
    for i in range(len(cat_var)):
        colList = []
        dataList = []
        d = var_prob[i] * baseProb_seri[cat_var[i]]/sm_num   # The chance of the small areas are considered equally
        for sa in small_areas:
            col_index = catNum * smallareaDict[sa] + dict_cat[cat_var[i]]
            colList.append(col_index)     
            dataList.append(d) 
        row = np.zeros(len(colList))
        col = np.array(colList)
        data = np.array(dataList)
        mat = csr_matrix((data,(row,col)), shape=(1,col_num))        
        result = result + mat  
    if cat_name == 'GENRE_NAME': 
        base_c = (delivery_base_g * baseProb_seri['宅配'] + other_base_g * baseProb_seri['その他のクーポン']
                 + hotel_base_g * baseProb_seri['ホテル・旅館'] + giftcard_base_g * baseProb_seri['ギフトカード']) 
        result = result + base_c
    # to be continued if cap is used
    return result

## tuning parameter are: alpha, tau
def userVec(df, cat_name, cuttime, alpha, tau):
    """
    Given a df for a certain user, create a vector (mainly composed of category and small area name) according to the history, 
    and the baseline.
    
    parameters
    ----------
    df: the dataframe used to calculate the vector
    cat_name: either "GENRE_NAME" or "CAPSULE_TEXT"
    cuttime: the cutting time, in the test situation, it should be datetime(2012, 6, 24)
    alpha: float, the combination coefficient of history and baseline. 
    tau: a float, the time constant for the exponential decay for the history
                 
    Returns
    -------
    A sparse vector for this user  
    """
    
    tn_total = len(df)            # total transaction time
    # print tn_total
    reg_time = df.REG_DATE[df.index[0]]     # The registration time
    # print reg_time
    if reg_time < datetime(2011, 7, 1):
        total_months = 12.0       # the months number that the user account holds
    else: 
        total_months = (cuttime - reg_time).days/30.0
    # print total_months
    # user_pfname = df.PREF_NAME[df.index[0]]
    history = userHistoryVec(df, cuttime, cat_name, tau)
    baseline = baseVec(df, cat_name)
    ## The scale factor of baseline, should be related to the number of transactions for this user
    beta = min(1.0, total_months/tn_total)        # 1/beta is the number of transactions per months to correct baseline
    # print beta                                              # and beta is initially constrained to be less than 1.0
    user_vec = alpha * history + beta * baseline  
    return user_vec

def userVec_v1(df, cat_name, cuttime, alpha, tau):
    """
    Given a df for a certain user, create a vector (mainly composed of category and small area name) according to the history, 
    and the baseline.
    
    parameters
    ----------
    df: the dataframe used to calculate the vector
    cat_name: either "GENRE_NAME" or "CAPSULE_TEXT"
    cuttime: the cutting time, in the test situation, it should be datetime(2012, 6, 24)
    alpha: float, the combination coefficient of history and baseline. 
    tau: a float, the time constant for the exponential decay for the history
                 
    Returns
    -------
    A sparse vector for this user  
    """
    
    tn_total = len(df)            # total transaction time
    # print tn_total
    reg_time = df.REG_DATE[df.index[0]]     # The registration time
    # print reg_time
    if reg_time < datetime(2011, 7, 1):
        total_months = 12.0       # the months number that the user account holds
    else: 
        total_months = (cuttime - reg_time).days/30.0
    # print total_months
    # user_pfname = df.PREF_NAME[df.index[0]]
    history = userHistoryVec(df, cuttime, cat_name, tau)
    baseline = baseVec(df, cat_name)
    ## The scale factor of baseline, should be related to the number of transactions for this user
    beta = total_months/tn_total        # 1/beta is the number of transactions per months to correct baseline
    # print beta                                              # and beta is not constrained to be less than 1.0
    user_vec = alpha * history + beta * baseline  
    return user_vec

#### Test code:
'''
cuttime = datetime(2012, 6, 24)
user_ID = 'd9dca3cb44bab12ba313eaa681f663eb'
user_ID = 'e78ae0887c4a9dce91ff0d2a45a9f72c'
user_df = uc_simple_wdates[uc_simple_wdates.USER_ID_hash == user_ID]
reg_time = user_df.REG_DATE[0]
tn_perMonth = (cuttime - reg_time).days/30.0
'''
### Coupon pre-analysis
coup_test_DISPFROM = pd.to_datetime(coupon_list_test['DISPFROM'])
coup_test_DISPEND = pd.to_datetime(coupon_list_test['DISPEND'])
coup_test_VALIDFROM = pd.to_datetime(coupon_list_test['VALIDFROM'])
coup_test_VALIDEND = pd.to_datetime(coupon_list_test['VALIDEND'])

coup_train_DISPFROM = pd.to_datetime(coupon_list_train['DISPFROM'])
coup_train_DISPEND = pd.to_datetime(coupon_list_train['DISPEND'])
coup_train_VALIDFROM = pd.to_datetime(coupon_list_train['VALIDFROM'])
coup_train_VALIDEND = pd.to_datetime(coupon_list_train['VALIDEND'])

coup_test = coupon_list_test.drop(['DISPFROM', 'DISPEND', 'VALIDFROM', 'VALIDEND'], axis = 1)
coup_test_wdates = coup_test.join(coup_test_DISPFROM).join(coup_test_DISPEND).join(coup_test_VALIDFROM).join(coup_test_VALIDEND)

coup_train = coupon_list_train.drop(['DISPFROM', 'DISPEND', 'VALIDFROM', 'VALIDEND'], axis = 1)
coup_train_wdates = coup_train.join(coup_train_DISPFROM).join(coup_train_DISPEND).join(coup_train_VALIDFROM).join(coup_train_VALIDEND)

def couponMat(coup_df, cat_name, endDate, rate_con, price_con):
    """
    Given a df for the coupon list, produce a coupon matrix that could multiply the user_vec to get
    the probability of each coupon being bought before the endDate. This is a simple version where 
    price factor is user independent.
    The price factor is calculated based on the price rate and discount price:
    (rate_con + pricerate)/(price_con + discount_price)
    
    parameters
    ----------
    coup_df: the coupon list being tested, e.g, coup_test_wdates
    cat_name: either "GENRE_NAME" or "CAPSULE_TEXT"
    endDate: the endDate of predicted time frame. (This could be used to calculate the probability of coupon 
    being bought during the timeframe)
    rate_con: float, rate constant
    price_con: float, discount price constant
                 
    Returns
    -------
    a sparse matrix: row dimension is the coupon number, column dimension is the same as user vector
    """
    coup_num = len(coup_df)
    row = np.arange(coup_num)        # The row number for the sparse matrix
    if cat_name == 'GENRE_NAME':
        dict_cat = genreDict
    else:
        dict_cat = capsuleDict
    catNum = len(dict_cat.keys())
    col_num = catNum * 55           # The column number for the sparse matrix
    ## The following code rearrange copy the coup_df and introduce new columns
    ## 1. The time probability column (should be less than 1): min(1.0, (endDate - DISPFROM)/DISPPERIOD)
    coup_df_new = pd.DataFrame.copy(coup_df)
    # a function that calculates the time interval between display from and endDate, assume the probability is linearly
    # dependent on the ratio between overlap interval and the display period
    interval = lambda x: float((endDate - x).days) 
    coup_df_new['Interval'] = coup_df_new['DISPFROM'].map(interval)
    timeRatio =  coup_df_new['Interval']/coup_df_new['DISPPERIOD']        
    coup_df_new['TimeProb'] = timeRatio.map(lambda x: min(1.0, x)) 
    ## Price adjustment:
    price_factor = price_con + coup_df_new['DISCOUNT_PRICE']  
    coup_df_new['priceAdjust'] = (rate_con + coup_df_new['PRICE_RATE'])/(price_factor * price_factor) * 1000.0 
    coup_df1 = coup_df_new.groupby([cat_name, 'small_area_name']).apply(normalize)
    coup_df1['totalProb'] = coup_df1['TimeProb'] * coup_df1['priceProb']
    colList = []
    data = coup_df1['totalProb'].values   # use total prob as the value, could be changed to other names
    # print data
    # print type(data)
    # print data.shape
    # print data.dtype
    for x in coup_df1.index:
        c_index = smallareaDict[coup_df1.small_area_name[x]] * catNum +  dict_cat[coup_df1[cat_name][x]]
        colList.append(c_index) 
    col = np.array(colList)
    result = csr_matrix((data,(row,col)), shape=(coup_num,col_num))
    return result


def normalize(df, column = 'priceAdjust', newcol = 'priceProb'):
    """
    Normalize the priceAdjust for each small_area_name and category
    """
    result = df
    df[newcol] = df[column]/(df[column].sum())
    return result
    
## Price info for the user that needs to be incorporated into the final tuning of coupon rank
# def priceHist(df, cat_dict):
    """
    Given a df for a certain user, calculate the mean and std of the price for a given bought
    coupon for a given category and small_area_name.
    
    parameters
    ----------
    df: the dataframe used to calculate the vector
    cat_dict: either "genreDict" or "capsuleDict"
                 
    Returns
    -------
    dataframe that has the category and small_area_name as index, and mean and std as the values
    """
    
# def coupon_udMat(coup_df, user_df, cat_name, endDate):
    """
    Given a df for the coupon list, produce a coupon matrix that could multiply the user_vec to get
    the probability of each coupon being bought before the endDate. Here price factor is user-dependent.
    
    parameters
    ----------
    coup_df: the coupon list being tested
    user_df: a df for a specific user
    cat_name: either "GENRE_NAME" or "CAPSULE_TEXT"
    endDate: the endDate of predicted time frame. (This could be used to calculate the probability of coupon 
    being bought during the timeframe)
                 
    Returns
    -------
    a sparse matrix  
    """

def userCoupList(user_vec, coup_mat, coup_df, topnum = 10):
    """
    Given a df for the coupon list and the user vector for a given user, produce the top 10 (or other number)
    of coupons from the coup list.
    
    parameters
    ----------
    coup_df: the coupon list being tested, e.g, coup_test_wdates
    coup_mat: the coupon matrix
    user_vec: user vector
    topnum: int, the number of coupons being predicted
                 
    Returns
    -------
    a dataframe of the coupons the user are most likely to buy
    """
    probList = coup_mat.dot(user_vec.T)
    row, col = probList.shape
    prob_seri = pd.Series(probList.toarray().reshape(row), index = coup_df.index)
    prob_seri.name = 'Probability'
    df = coup_df.join(prob_seri)
    result = df.sort(['Probability'], ascending = False)[:topnum]
    return result       ## result['COUPON_ID_hash'].values is the array of coupon list

def rankList(startT, endT, pstartT, pendT, user_ID, df):
    """
    A list of top ten ranked coupons for a given user depending on the history period used
    
    Typically, the prediction time should be a week.
    
    parameters
    ----------
    df: the dataframe used to calculate the vector
    
    startT : the starting date of the history period considered
             
    endT : the end date of the history period considered
    
    pstartT: the starting date of the prediction period
    
    pendT: the end date of the prediction period
    
    user_ID: user_ID hash value
                 
    Returns
    -------
    A ranked list of coupon_IDs
    """
    user_df = df[df.USER_ID == user_ID]
    if valid(user_ID) == 0: 
        return []
        
### Useful functions in testing codes, not a very good working function yet!:
def dfSelect(df, timePoint, startT, endT):
    """
    A list of coupons provided given a period of time 
    
    parameters
    ----------
    df: should be a dataframe that has coupon display information.
    
    timePoint: string, the date of timePoint, e.g ('DISPFROM') from the coupon feature 
    
    startT: datetime, the start time of the coupon (included)
    endT: datetime, the end time of the coupon (excluded)
                     
    Returns
    -------
    A dataframe of coupon information (including hash values) for the conditions provided
    """
    df1 = df[df[timePoint] >= startT]
    df2 = df1[df1[timePoint] < endT]
    num = len(df2)
    # print num
    # reindex the dataframe so it starts from 0.
    df3 = pd.DataFrame(data=df2.values,columns=df2.columns,index=(range(num)))             
    return df3
    
def dfSelect_v1(df, timePoint, startT, endT):
    """
    A list of coupons provided given a period of time 
    
    parameters
    ----------
    df: should be a dataframe that has coupon display information.
    
    timePoint: string, the date of timePoint, e.g ('DISPFROM') from the coupon feature 
    
    startT: datetime, the start time of the coupon (included)
    endT: datetime, the end time of the coupon (excluded)
                     
    Returns
    -------
    A dataframe of coupon information (including hash values) for the conditions provided
    """
    df1 = pd.DataFrame.copy(df[df[timePoint] >= startT])
    df2 = df1[df1[timePoint] < endT]
    # num = len(df2)
    # print num
    # reindex the dataframe so it starts from 0.
    # df3 = df2.reindex(index = range(num), columns = df2.columns)             
    return df2
    
def baseVec_noHist(df, cat_name):
    """
    Given a user has no history, create a vector (mainly composed of category and small area name) according to basic information
    of the user (mainly PREF name, SEX_ID, initially). If no PREF info is available, a universal basevec would be used
    
    General strategy: For the categories that have low correlation with the user's location, the values are largely calculated above
    For the categories have a relatively high correlation with the user's location, pref_name is used. Otherwise, if the pref_name is 
    naN, then a universal vector would be created
    
    parameters
    ----------
    df: the dataframe for this user which is used to calculate the vector, user_list would be the one here.
    cat_name: either "GENRE_NAME" or "CAPSULE_TEXT"       
    Returns
    -------
    a sparse vector
    """
    sex = df.SEX_ID[df.index[0]]
    if sex == 'f':
        if cat_name == 'GENRE_NAME':
            baseProb_seri = baseProb_f_g       # baseline probability for female 
        else: 
            baseProb_seri = baseProb_f_cap
    else:
        if cat_name == 'GENRE_NAME':
            baseProb_seri = baseProb_m_g
        else: 
            baseProb_seri = baseProb_m_cap      # baseline probability for male
    dict_cat = {}
    if cat_name == 'GENRE_NAME':
        dict_cat = genreDict
    else:
        dict_cat = capsuleDict
    catNum = len(dict_cat.keys())
    col_num = catNum * 55 
    result = csr_matrix((1,col_num))  
    user_pfname = df.PREF_NAME[df.index[0]]
    if ((type(user_pfname) != str) and math.isnan(user_pfname)): 
        #small_areas = df.SMALL_AREA_NAME.unique()
        #var_prob = cat_var_prob_sm
        result = csr_matrix((1,col_num))
        for i in range(len(cat_var)):
            result = result + baseProb_seri[cat_var[i]] * cat_base(uc_simple, cat_name, cat_var[i])   
    else:
        small_areas = np.array(ks_dict[user_pfname])
        var_prob = cat_var_prob
        sm_num = len(small_areas) 
        for i in range(len(cat_var)):
            colList = []
            dataList = []
            d = var_prob[i] * baseProb_seri[cat_var[i]]/sm_num   # The chance of the small areas are considered equally
            for sa in small_areas:
                col_index = catNum * smallareaDict[sa] + dict_cat[cat_var[i]]
                colList.append(col_index)     
                dataList.append(d) 
            row = np.zeros(len(colList))
            col = np.array(colList)
            data = np.array(dataList)
            mat = csr_matrix((data,(row,col)), shape=(1,col_num))        
            result = result + mat  
    if cat_name == 'GENRE_NAME': 
        base_c = (delivery_base_g * baseProb_seri['宅配'] + other_base_g * baseProb_seri['その他のクーポン']
                 + hotel_base_g * baseProb_seri['ホテル・旅館'] + giftcard_base_g * baseProb_seri['ギフトカード']) 
        result = result + base_c
    # to be continued if cap is used
    return result



def lws_initializeDFs(startT, endT):
    """
    initialize the dataframes from a certain week of the last few weeks
    
    parameters
    ----------
    starT: datetime, starting time of the week
    endT: datetime, ending time of the week
                 
    Returns
    -------
    A dictionary, including the coup_list for this week, the uc info, transations, tain data
    user_ID and their bought coupons
    """
    dict = {}
    dict['coup_list'] = dfSelect_v1(coup_train_wdates, 'DISPFROM', startT, endT)
    dict['uc_simple_lws'] = dfSelect(uc_simple_wdates, 'DISPFROM', startT, endT)
    dict['trans_lws'] = dfSelect(dict['uc_simple_lws'] , 'I_DATE', startT, endT)
    startT_train = datetime(2011, 7, 1)
    endT_train = startT
    dict['uc_train_lws'] = dfSelect(uc_simple_wdates, 'I_DATE', startT_train, endT_train)
    trans_lw = dict['trans_lws']
    lw_users = trans_lw['USER_ID_hash'].unique() 
    uc_lw_dict = {}
    trans_lw = dict['trans_lws']
    for x in lw_users:
        user_lw = trans_lw[trans_lw.USER_ID_hash == x]
        uc_lw_dict[x] = user_lw['COUPON_ID_hash'].unique()
    dict['uc_dict'] = uc_lw_dict  
    return dict


## Visiting data added
## A complete info for both the visit info and coupon info
## Code part
coup_visit_complete = pd.merge(coupon_visit_train, coupon_list_train, left_on = 'VIEW_COUPON_ID_hash', right_on = 'COUPON_ID_hash', sort = False)
uvisit_simple = coup_visit_complete[['PURCHASE_FLG','USER_ID_hash', 'VIEW_COUPON_ID_hash', 'CAPSULE_TEXT','GENRE_NAME', 'PRICE_RATE', 'DISCOUNT_PRICE','ken_name', 'small_area_name']]

# Convert all dates to datetime format. 
uvisit_I_DATE = pd.to_datetime(coup_visit_complete['I_DATE'])
uvisit_DISPFROM = pd.to_datetime(coup_visit_complete['DISPFROM'])
uvisit_DISPEND = pd.to_datetime(coup_visit_complete['DISPEND'])
uvisit_VALIDFROM = pd.to_datetime(coup_visit_complete['VALIDFROM'])
uvisit_VALIDEND = pd.to_datetime(coup_visit_complete['VALIDEND'])

## Add the dates on
uvisit_simple_wdates = uvisit_simple.join(uvisit_I_DATE).join(uvisit_DISPFROM).join(uvisit_DISPEND).join(uvisit_VALIDFROM).join(uvisit_VALIDEND)
#uvisit_simple_wdates[uvisit_simple_wdates.PURCHASE_FLG == 1].info()

## Only not purchased coupons are considered as the other history took care of the purchased coup
uvisit_only_simple_wdates = uvisit_simple_wdates[uvisit_simple_wdates.PURCHASE_FLG == 0]

def userVisitVec(df, cuttime, cat_name, tau_visit):
    """
    Given a visiting df for this user, create a vector (mainly composed of category and small area name) 
    according to his/her visiting history. 
    
    parameters
    ----------
    df: the dataframe for this user which is used to calculate the vector
    cat_name: either "GENRE_NAME" or "CAPSULE_TEXT"
    cuttime: the cutting time, in the test situation, it should be datetime(2012, 6, 24)
    tau_visit: a float, the time constant for the exponential decay for the history
               
    Returns
    -------
    A sparse vector that  
    """
    df1 = df.drop_duplicates(['VIEW_COUPON_ID_hash'])    # only unique coupons are being counted
    dict_cat = {}
    if cat_name == 'GENRE_NAME':
        dict_cat = genreDict
    else:
        dict_cat = capsuleDict
    catNum = len(dict_cat.keys())
    col_num = catNum * 55       ## 55 is the total names of small_area_name
    result = csr_matrix((1,col_num))          ## initialize an empty 1 * col_num sparse matrix 
    df_index = df1.index
    for x in df_index:
        catName = df1[cat_name][x]
        smallArea = df1.small_area_name[x]
        j = dict_cat[catName]
        i = smallareaDict[smallArea]
        date = df1.I_DATE[x]
        timespan = (cuttime - date).days   ## number of days past since the cuttime
        # print timespan
        data = np.array([1.0])
        col = np.array([i * catNum + j])
        row = np.array([0])
        mat = csr_matrix((data,(row,col)), shape=(1,col_num))
        result = result + exp(-timespan/tau_visit) * mat
    return result

def userVec_wVisit(df, df_visit, cat_name, cuttime, alpha, tau, alpha_visit, tau_visit):
    """
    Given a df for a certain user, create a vector (mainly composed of category and small area name) according to the history, 
    and the baseline.
    
    parameters
    ----------
    df: the purchasing dataframe used to calculate the vector
    df_visit: the visiting history used to calculate the vector
    cat_name: either "GENRE_NAME" or "CAPSULE_TEXT"
    cuttime: the cutting time, in the test situation, it should be datetime(2012, 6, 24)
    alpha: float, the combination coefficient of history and baseline. 
    alpha_visit: float, the coefficient of visit relative to history and baseline
    tau: a float, the time constant for the exponential decay for the history
    tau_visit, a float, the time constant for the exponential decay for the visiting history
                 
    Returns
    -------
    A sparse vector for this user  
    """
    
    tn_total = len(df)            # total transaction time
    # print tn_total
    reg_time = df.REG_DATE[df.index[0]]     # The registration time
    # print reg_time
    if reg_time < datetime(2011, 7, 1):
        total_months = 12.0       # the months number that the user account holds
    else: 
        total_months = (cuttime - reg_time).days/30.0
    # print total_months
    # user_pfname = df.PREF_NAME[df.index[0]]
    history = userHistoryVec(df, cuttime, cat_name, tau)
    visit = userVisitVec(df_visit, cuttime, cat_name, tau_visit)
    baseline = baseVec(df, cat_name)
    ## The scale factor of baseline, should be related to the number of transactions for this user
    beta = min(1.0, total_months/tn_total)        # 1/beta is the number of transactions per months to correct baseline
    # print beta                                              # and beta is initially constrained to be less than 1.0
    user_vec = alpha * history + beta * baseline + alpha_visit * visit
    return user_vec
    
def lws_initializeDFs_wVisit(startT, endT):
    """
    initialize the dataframes from a certain week of the last few weeks
    
    parameters
    ----------
    starT: datetime, starting time of the week
    endT: datetime, ending time of the week
                 
    Returns
    -------
    A dictionary, including the coup_list for this week, the uc info, transations, tain data
    user_ID and their bought coupons
    """
    dict = {}
    dict['coup_list'] = dfSelect_v1(coup_train_wdates, 'DISPFROM', startT, endT)
    dict['uc_simple_lws'] = dfSelect(uc_simple_wdates, 'DISPFROM', startT, endT)
    dict['trans_lws'] = dfSelect(dict['uc_simple_lws'] , 'I_DATE', startT, endT)
    startT_train = datetime(2011, 7, 1)
    endT_train = startT
    dict['uc_train_lws'] = dfSelect(uc_simple_wdates, 'I_DATE', startT_train, endT_train)
    dict['uvisit_train_lws'] = dfSelect(uvisit_only_simple_wdates, 'I_DATE', startT_train, endT_train)
    trans_lw = dict['trans_lws']
    lw_users = trans_lw['USER_ID_hash'].unique() 
    uc_lw_dict = {}
    trans_lw = dict['trans_lws']
    for x in lw_users:
        user_lw = trans_lw[trans_lw.USER_ID_hash == x]
        uc_lw_dict[x] = user_lw['COUPON_ID_hash'].unique()
    dict['uc_dict'] = uc_lw_dict  
    return dict
    


## initialize the parameters

#rate_con = 1.0
#price_con = 1000.0

gc.collect()

## Visiting history added
def main_check_wVisit(startT, endT, cat_name, alpha, tau, alpha_visit, tau_visit, rate_con, price_con):
    """
    Given the week info, find out the precision
    """
    print str(startT)[:10], "a,t,av,tv", alpha, tau, alpha_visit, tau_visit, " starts @", datetime.now()
    
    #initialize dict
    dict = lws_initializeDFs_wVisit(startT, endT)

    
    #continue the work!
    cuttime = startT
    endDate = endT + timedelta(1)
    coup_list = dict['coup_list']
    uc_dict = dict['uc_dict']
    uc_train_lw = dict['uc_train_lws']
    uvisit_train_lw = dict['uvisit_train_lws']    # add visiting history
    coup_mat = couponMat(coup_list, cat_name, endDate, rate_con, price_con)
    score = 0.0
    preList = []
    user_ID = []       # user information could be retrieved later
    noHist = 0
    nonzero = 0.0
    
    
    for x in uc_dict.keys():
        user_ID.append(x)
        user_coup_df = uc_train_lw[uc_train_lw.USER_ID_hash == x]
        uvisit_df = uvisit_train_lw[uvisit_train_lw.USER_ID_hash == x] 
        purchNum = len(user_coup_df)    
        if len(user_coup_df) == 0:
            user_df = user_list[user_list.USER_ID_hash == x]    # user_ID is used here
            user_vec = baseVec_noHist(user_df, cat_name)
        else: 
            user_vec = userVec(user_coup_df, cat_name, cuttime, alpha, tau)
        ## The following part consider the visit history
        if len(uvisit_df) != 0:
            user_visit_vec = userVisitVec(uvisit_df, cuttime, cat_name, tau_visit)
            modify_coeff = int(purchNum)/9 + 1
            user_vec = user_vec + alpha_visit * user_visit_vec / float(modify_coeff)
        coup_predict_df = userCoupList(user_vec, coup_mat, coup_list, topnum = 10)
        coup_predict = list(coup_predict_df['COUPON_ID_hash'].values)
            #print coup_predict
        pre = meanPrecision.apk(list(uc_dict[x]), coup_predict, k=10)
            #print pre
        if pre != 0.0:
            nonzero = nonzero + 1
        preList.append(pre)
        score = score + pre
    result_data = {'user_ID': np.array(user_ID), 'precision': np.array(preList)} 
    result_df = pd.DataFrame(result_data)
    filename = 'lws_stats_mv/' + str(startT)[:10] + 'alpha' + str(alpha) + 'tau' + str(tau) + 'alphaV' + str(alpha_visit) + 'tauV' + str(tau_visit) + 'rate_con' + str(rate_con) + 'price_con' + str(price_con) + '.csv'
    result_df.to_csv(filename)
    print str(startT)[:10], "a,t,av,tv", alpha, tau, alpha_visit, tau_visit, " ends @", datetime.now()
    return (score, nonzero)




 


## Testing code
if __name__ == '__main__':

    startT_coup_lw1 = datetime(2012, 6, 17)
    endT_coupL_lw1 = datetime(2012, 6, 24)
    
    tau = 240.0
    alpha = 0.5
    tau_visit = 240.0
    alpha_visit = 0.3    
    startT = startT_coup_lw1
    endT = endT_coupL_lw1
    
    res =  main_check_wVisit(startT, endT, 'GENRE_NAME', alpha, tau, alpha_visit, tau_visit)
    print "score, nonzero = ", res
  
    print "program ends @", datetime.now() 
 


    
    
