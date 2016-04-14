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
####

#import meanPrecision
import pandas as pd
import numpy as np
#from scipy.sparse import csr_matrix
from datetime import datetime
from math import exp
import math
from multiprocessing import Pool #, Process, Lock
import time
from main_check_wVisit_priceSquare_v1 import main_check_wVisit

# change the following for specific weeks, counted from the last week
# [1,2] means the last two weeks
lastWeeks = [2,4,6]
lWeekRange = [i-1 for i in lastWeeks] 


#tau_arr = [7.0, 10.0, 14.0, 30.0, 60.0, 90.0, 120.0, 240.0, 260.0, 500.0, 1000.0, 5000.0]
#tau_arr = [7.0, 10.0, 14.0, 30.0, 60.0, 90.0, 120.0, 240.0, 260.0, 280.0, 300.0, 320.0, 340.0, 360.0, 400.0, 500.0, 1000.0, 5000.0]
#alpha_arr = [0.0001, 0.0005, 0.001, 0.002, 0.005, 0.01, 0.02, 0.05, 0.1, 0.2, 0.5, 0.8, 1.0, 1.2, 1.5, 2.0, 5.0, 10.0]
rate_con_arr = [1.0, ]
price_con_arr = [-90.0, ]

tau_arr = [300, ]
alpha_arr = [0.8,]

tau_visit_arr = [300, ]
alpha_visit_arr = [1.0, 1.2]

startT_coup_lw1 = datetime(2012, 6, 17)
endT_coupL_lw1 = datetime(2012, 6, 24)

startTList = [startT_coup_lw1- pd.Timedelta(weeks = i) for i in lWeekRange]
endTList = [endT_coupL_lw1 - pd.Timedelta(weeks = i) for i in lWeekRange]

def workFunction(i):    
   #to process a week's data, save the result into a file named for the week!
    print 'worker',i,'starts'
    alpha_list = []
    tau_list = []
    alpha_visit_list = []
    tau_visit_list = []
    rate_con_list = []
    price_con_list = []
    score_list = []
    nonzero_list = []
    startT = startTList[i]
    endT = endTList[i]
    filename = 'lws_stats_mv/Result' + str(startT)[:10] + '.csv'

    for rate_con in rate_con_arr:
        for price_con in price_con_arr:
            for tau in tau_arr:
                for alpha in alpha_arr:
                    for tau_visit in tau_visit_arr:
                        for alpha_visit in alpha_visit_arr:  
                            res =  main_check_wVisit(startT, endT, 'GENRE_NAME', alpha, tau, alpha_visit, tau_visit, rate_con, price_con)
                            alpha_list.append(alpha)
                            tau_list.append(tau)
                            alpha_visit_list.append(alpha_visit)
                            tau_visit_list.append(tau_visit)
                            rate_con_list.append(rate_con)
                            price_con_list.append(price_con)
                            score_list.append(res[0])
                            nonzero_list.append(res[1])      
                            #please add code here to write the statistics to a file             
    result_data = {'alpha': np.array(alpha_list), 'tau': np.array(tau_list), 'alpha_v': np.array(alpha_visit_list), 'tau_v': np.array(tau_visit_list), 'rate_c': np.array(rate_con_list), 'price_c': np.array(price_con_list),'score': np.array(score_list),'nonzero': np.array(nonzero_list)} 
    result_df = pd.DataFrame(result_data)
    result_df.to_csv(filename)
    print 'worker',i,'ends'




if __name__ == '__main__':
  
    print "program starts @", datetime.now()
    
    pool = Pool(processes =  3) 
# I have a 8-core cpu, therefore use 6 core for this app, leaving 2 for windows
# with 6 process, cpu running at 80-90 % level
#important note: 
#gloables will be created for each process. e.g. 2 processes = 3 copies of gloables
# for this program, I find that initially 2-3 processes will take all the momories 
# However, it seems that windows will manage memory after a while, dropping from 7.9G to 4.8G in 10 min    

    for i in range(len(lWeekRange)):
        pool.apply_async(workFunction, args=(i,))
                
    pool.close()
    pool.join()
    print "program ends @", datetime.now() 
 


    
    
