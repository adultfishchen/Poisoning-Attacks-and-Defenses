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
import datetime
import warnings

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import sumolib
def AverageSpeedAllData(inputdir,outputdir,lane,filenum):

    total = 0
    flag =0
    for outeridx in range(filenum):
        try:
            tempAvg_data = pd.read_csv(inputdir+str(outeridx)+"/"+lane+".csv")
            total += 1
        except:
            #print("Average File "+lane+".csv not exist")
            continue
        if flag ==0:
            
            avg_data = tempAvg_data
            avg_intervel= tempAvg_data["interval"]
            flag =1
            #print(len(avg_data))
        else:
            if len(avg_data) >= len(tempAvg_data):
                avg_data += tempAvg_data.reindex_like(avg_data).fillna(13.89)
            else:
                avg_data = avg_data.reindex_like(tempAvg_data).fillna(13.89) + tempAvg_data
                avg_intervel = tempAvg_data["interval"]

        #count_mean = np.isinf(avg_data).values.sum()
        #if  count_mean>0:
        #    print(outeridx)
    #a = avg_data["avgspeed"].tolist()

    #for i,b in enumerate(a):
    #    print("i= ",i)
    #    print(b)

    if total==0:
        return
    avg_data /= total
    avg_data["interval"] = avg_intervel
    avg_data = avg_data.groupby("interval",as_index=False).mean()
    avg_data.to_csv(outputdir+"/"+lane+"_mean.csv", index=False)


def GetMinMax(data_len):
    return max(data_len) , min(data_len)

def MakePdAndDict(data_max,data_min,columns):
    Index_list = []
    Num_dict = {}
    
    for i in range(data_min,data_max):
        Num_dict[i] = 0
        Index_list.append(i)

    df = pd.DataFrame(columns = columns, 
                   index = Index_list)
    df = df.fillna(0) 
    return df , Num_dict

def AverageZAllData(inputdir,outputdir,lane,filenum):

    #inst_len = []
    sel_len = []
    flag = 0
    total = 0
    for outeridx in range(filenum):
        try:
            #tempAvginst_data = pd.read_csv(inputdir+"/"+lane+"_"+str(outeridx)+".csv")
            #inst_len.append(len(tempAvginst_data))
            #print(inputdir+str(outeridx)+"/SelectSpeed_"+lane+".csv")
            tempSelected_data = pd.read_csv(inputdir+str(outeridx)+"/SelectSpeed_"+lane+".csv")
            sel_len.append(len(tempSelected_data))

        except:
            #print(inputdir+str(outeridx)+"/SelectSpeed_"+lane+".csv not exist")
            continue
    #inst_max ,inst_min = GetMinMax(inst_len)
    if not sel_len:
        return
    sel_max , sel_min = GetMinMax(sel_len)
    #columns = tempAvginst_data.columns.values.tolist()
    #inst_total_df, inst_num_dict = MakePdAndDict(inst_max,inst_min,columns)
    columns = tempSelected_data.columns.values.tolist()
    sel_total_df , sel_num_dict = MakePdAndDict(sel_max,sel_min,columns)

    for outeridx in range(filenum):
        try:
            #tempAvginst_data = pd.read_csv(inputdir+"/"+lane+"_"+str(outeridx)+".csv")
            tempSelected_data = pd.read_csv(inputdir+str(outeridx)+"/SelectSpeed_"+lane+".csv")

        except:
            #print(inputdir+str(outeridx)+"/SelectSpeed_"+lane+".csv not exist")
            continue
        if flag ==0:
            '''
            if len(tempAvginst_data) > inst_min:
                avginst_data = tempAvginst_data[:inst_min]

            for i in range(inst_min,len(tempAvginst_data) ):
                inst_total_df.loc[i] += tempAvginst_data.iloc[i]
                inst_num_dict[i] += 1
            '''
            if len(tempSelected_data) >= sel_min:
                Selected_data = tempSelected_data[:sel_min]

            for i in range(sel_min,len(tempSelected_data) ):
                sel_total_df.loc[i] += tempSelected_data.iloc[i]
                sel_num_dict[i] += 1
            flag = 1
            total += 1
        else:
            '''
            if len(tempAvginst_data) > inst_min:
                avginst_data += tempAvginst_data[:inst_min]

            for i in range(inst_min,len(tempAvginst_data) ):
                inst_total_df.loc[i] += tempAvginst_data.iloc[i]
                inst_num_dict[i] += 1
            '''
            if len(tempSelected_data) >= sel_min:
                Selected_data += tempSelected_data[:sel_min]

            for i in range(sel_min,len(tempSelected_data) ):
                sel_total_df.loc[i] += tempSelected_data.iloc[i]
                sel_num_dict[i] += 1
            total += 1

    #avginst_data /= filenum
    Selected_data /= total
    '''
    for i in range(inst_min,inst_max):
        inst_total_df.loc[i] /=inst_num_dict[i]
        avginst_data.append(inst_total_df)
    '''
    for i in range(sel_min,sel_max):
        sel_total_df.loc[i] /=sel_num_dict[i]
        Selected_data = Selected_data.append(sel_total_df.loc[i])

    #avginst_data["interval"] = avginst_data["interval"].astype(int)
    #Selected_data["interval"] = Selected_data["interval"].astype(int)
    #avginst_data.to_csv(outputdir+"/avginst_"+lane+"_mean.csv", index=False)
    Selected_data.to_csv(outputZdir+"/selected_"+lane+"_mean.csv", index=False)



if __name__ == "__main__":
    
    ST = datetime.datetime.now()
    
    print("Final...")
    NetName = "data/01/Tainan.net.xml"
    net = sumolib.net.readNet(NetName)
    edges = net.getEdges()
    Lane_list = []
    #'''
    for edge in edges:
        lanes = edge.getLanes()
        for lane in lanes:
            Lane_list.append(lane.getID())
            #Lane_dict[lane.getID()] = lane.getLength()
    #'''
    #Lane_list.append("319713269#3_1")
    #Lane_dict[] = 5
    
    inputdir = 'interavg_result/out'
    outputdir = 'finalavg_result/'
    if not os.path.exists(outputdir):
        os.makedirs(outputdir)
    inputZdir = 'interZ_result/out'
    outputZdir = 'finalZ_result/'
    if not os.path.exists(outputZdir):
        os.makedirs(outputZdir)
    
    warnings.filterwarnings("ignore")
    for lane in Lane_list:
        AverageSpeedAllData(inputdir,outputdir,lane,10)
        AverageZAllData(inputZdir,outputZdir,lane,10)
    
    ED = datetime.datetime.now()

    time_series = ED-ST
    Tlog = "Time for executing finalavg.py　=> " + str(time_series)+"\n"
    wf = open("Timer/timer.txt" , mode='a')    
    wf.write(Tlog)
    wf.close()
    
