# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import optparse
import csv
import math
from random import sample
import pandas as pd
import numpy as np
from tensorflow.keras import optimizers
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout, Activation, Flatten, LSTM, TimeDistributed, RepeatVector
#from tensorflow.keras.layers.normalization import BatchNormalization
from tensorflow.keras.optimizers import Adam
from tensorflow.keras.optimizers import SGD
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.callbacks import EarlyStopping, ModelCheckpoint
import matplotlib.pyplot as plt
import os
import math
import datetime

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import sumolib

'''
arr2= np.array([[4, 2, 3, 2, 1, 8], 
               [5, 4,6,7,8,9]]) 
res = np.shape(arr2)
print(res)

---> (2,6)
'''
def build_data(data, past, shift, x, y):
    for i in range(0, data.shape[0]-past, shift):
        # 4 in a group, and shifted by 1 step
        # the front 3 as features, and the next as label
        x.append(np.array(data.iloc[i:i+past]))#['inst_speed']
        y.append(np.array(data.iloc[i+past]))#['inst_speed']
    return x , y
def count(lane , x , y):
    data = pd.DataFrame(columns=["inst_speed"])
    
    end = 45
    start = 10
    '''
    end = 25
    start = 10
    '''
    inputdir = 'interavg_result/out'
    meanfolder_path = 'finalavg_result'
    
    for i in range(start,end):
            try: #���ǹD�� �t�׳���0 �]���N���h��
                data = pd.read_csv(inputdir+str(i)+"/"+lane+".csv")
                data = data.drop(columns="interval")
                data = data.drop(columns="avgspeed")
                mean = pd.read_csv(meanfolder_path+"/"+lane+"_mean.csv")
                mean = mean.drop(columns="interval")
                data = data.round(3)
                
                if len(data) > len(mean):
                    data["instspeed"][:len(mean)] -= mean["instspeed"]
                else:
                    data["instspeed"] -= mean["instspeed"]
                    
                if data["instspeed"].isnull().values.any():
                    print(inputdir+str(i)+"/"+lane+".csv")
                    print("up")
                    exit(0)
                if mean["instspeed"].isnull().values.any():
                    print(meanfolder_path+"/"+lane+"_mean.csv")
                    print("up2")
                    exit(0)
                count_data = np.isinf(data).values.sum()
                if  count_data >0:
                    print("inf1")
                    for b in data["instspeed"].tolist():
                        print(b)
                    print(inputdir+str(i)+"/"+lane+".csv")
                    exit(0)
                count_mean = np.isinf(mean).values.sum()
                if  count_mean>0:
                    print("inf2")
                    print(meanfolder_path+"/"+lane+"_mean.csv")
                    exit(0)
                
                #print(data)
               
                
                x, y = build_data(data, 3, 1, x, y)
                #x = np.array(data)
                if np.any(np.isinf(x)):
                    print(inputdir+str(i)+"/"+lane+".csv")
                    exit(0)
                if np.any(np.isnan(x)):
                    print(inputdir+str(i)+"/"+lane+".csv")
                    exit(0)
                
            except Exception as e:
                #print(e)
                #return x , y
                pass
                
    return x , y

if __name__ == "__main__":

    ST = datetime.datetime.now()
    print("Train Start at：",ST)
    
    outputdir = "models"
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    NetName = "data/01/Tainan.net.xml"
    net = sumolib.net.readNet(NetName)
    edges = net.getEdges()
    #LaneList = []
    
    
    for edge in edges:
        
        
        
        x = []
        y = []
        
        lanes = edge.getLanes()
        for lane in lanes:
            x , y = count(lane.getID() , x , y)
        if len(x) <= 100 or len(y) <=100:
            continue
        
        #start = perf_counter()

        x = np.array(x)
        y = np.array(y)
        
        X_train, X_valid, y_train, y_valid = train_test_split(x, y, test_size=0.2)
        if np.any(np.isinf(X_train)):
            exit(0)
        if np.any(np.isinf(y_train)):
            exit(0)
        if np.any(np.isinf(X_valid)):
            exit(0)
        if np.any(np.isinf(y_valid)):
            exit(0)
        
        model = Sequential()
        model.add(LSTM(64, input_length=x.shape[1], input_dim=x.shape[2], return_sequences=True))
        model.add(Dropout(0.3))
        model.add(LSTM(64, return_sequences=True))
        model.add(Dropout(0.2))
        model.add(LSTM(32, return_sequences=False))
        model.add(Dropout(0.2))
        model.add(Dense(1))
        
        '''
        opti = optimizers.Adam(lr=0.001, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)
        
        opti = optimizers.Adam(lr=0.01, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)
        opti = optimizers.Adam(lr=0.0005, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)
        
        opti = optimizers.Adam(lr=0.005, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)

        opti = optimizers.Adam(lr=0.05, beta_1=0.9, beta_2=0.999, epsilon=None, decay=0.0, amsgrad=False)
        '''
        model.compile(loss = 'mse', optimizer = 'adam' )#'adam' 'SGD' opti
        model.summary()
        
        
        
        callback = EarlyStopping(monitor="loss", patience=10, verbose=1, mode="auto")
        history = model.fit(X_train, y_train, validation_data=(X_valid,y_valid), epochs = 50, callbacks=[callback]) # epochs = 50, 30
        
        mode_name = edge.getID()+"_model.h5"
        model.save("models/"+mode_name)

    ED = datetime.datetime.now()
    print("Train end at：",ED)
    time_series = ED-ST
    print(ED-ST)
    Tlog = "Time for executing train.py　=> " + str(time_series)+"\n"
    wf = open("Timer/timer.txt" , mode='a')    
    wf.write(Tlog)
    wf.close()