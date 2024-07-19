from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import optparse
from optparse import OptionParser
import csv
import math
from random import sample
import pandas as pd
import numpy as np
import statistics as st
import datetime

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import sumolib
        
        
def cal_avg(data):
    veh_avg = []
    
    for j in range(len(data)):
        t = abs(data.iloc[j]["real_exit"]-data.iloc[j]["real_entry"])
        a= data.iloc[j]["length"]/t
        veh_avg.append(a)
    
                
    return veh_avg

def tamper_vehavg(data):
    tamper_vehavg = []
    
    for j in range(len(data)):
        t = abs(data.iloc[j]["exit"]-data.iloc[j]["entry"])
        a= data.iloc[j]["length"]/t
        tamper_vehavg.append(a)
    
                
    return tamper_vehavg

def target_category(data):
    target = []
    
    for j in range(len(data)):
        
        if data.iloc[j]["instspeed"] == data.iloc[j]["real_instspeed"]:
             
            target.append(1)
        else:
            
            target.append(0)
    
                
    return target

if __name__ == "__main__":
    
    ST = datetime.datetime.now()
    
    parser = OptionParser()#parser = OptionParser()
    parser.add_option("-s", "--start", dest="start", type="int" ,default="-1", help="The start used to run SUMO start from txt_result/outx")
    parser.add_option("-e", "--end", dest="end", type="int" ,default="-1", help="The end used to run SUMO end at txt_result/outx")
    (options, args) = parser.parse_args()
    start = options.start
    end = options.end


        
    NetName = "data/01/Tainan.net.xml"
    net = sumolib.net.readNet(NetName)
    edges = net.getEdges()
    Lane_dict = {}
    #'''
    for edge in edges:
        lanes = edge.getLanes()
        for lane in lanes:
            Lane_dict[lane.getID()] = lane.getLength()
    #'''
    #Lane_dict["-111343195#2_0"] = 5
    print("Defense begin......")
    for i in range(start,end):
        if not os.path.exists('defense/out'+str(i)):
            os.makedirs('defense/out'+str(i))
        print("i = ",i)
        for lane in Lane_dict.keys():       
            try:
                esti_data = pd.read_csv('concat/out'+str(i)+"/"+lane +".csv")
                #ref = pd.read_csv("Reference/"+out'+str(i)+"/_relationships_defense.csv")
                    
                esti_data["veh_avg"] = cal_avg(esti_data)
                esti_data["tamper_vehavg"] = tamper_vehavg(esti_data)
                esti_data["target"] = target_category(esti_data)
                esti_data.to_csv("defense/out"+str(i)+"/"+lane+".csv" , index=False)
            except OSError as e:
                #print(e)
                pass
                
    ED = datetime.datetime.now()

    time_series = ED-ST
    Tlog = "Time for executing defense.py　=> " + str(time_series)+"\n"
    wf = open("Timer/timer.txt" , mode='a')    
    wf.write(Tlog)
    wf.close()

        
