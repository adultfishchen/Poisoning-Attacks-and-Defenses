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
    vehavg = []
    
    for j in range(len(data)):
        t = abs(data.iloc[j]["exit"]-data.iloc[j]["entry"])
        a= data.iloc[j]["length"]/t
        vehavg.append(a)
    
                
    return vehavg

def target_category(data,ref):
    target = []
    try:
      a = ref.loc[ref['Lane'] == lane]['coefficient_1'].tolist()
      b = ref.loc[ref['Lane'] == lane]['coefficient_2'].tolist()
      c = ref.loc[ref['Lane'] == lane]['intercept'].tolist()
      
      for j in range(len(data)):
          
          if (float(a[0])*data.iloc[j]["instspeed"]+float(b[0])*data.iloc[j]["tamper_vehavg"] + float(c[0]) < 0):
               
              target.append(0)
          else:
              
              target.append(1)
    except IndexError as e:
      #print(e)
      pass
    except KeyError as e:
      #print(e)
      pass
    
                
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
    
    lane_list = ["-496253687#1_0","250710099#0_0","-24452786#6_0","-160253722#7_0","-24452786#2_0","71285598#5_0","108037210#0_0","-496332201#4_0","-286094870#6_0","-227913938#10_0","307096544#4_0"]
    
    print("Defense begin......")
    for i in range(start,end):
        if not os.path.exists('defense/out'+str(i)):
            os.makedirs('defense/out'+str(i))
        print("i = ",i)
        #for lane in Lane_dict.keys():
        for lane in lane_list:       
            try:
                esti_data = pd.read_csv('csv_result/out'+str(i)+"/"+lane +".csv")
                ref = pd.read_csv("Reference/relationships_defense.csv")
                
                
                esti_data["veh_avg"] = cal_avg(esti_data)
                esti_data["tamper_vehavg"] = esti_data["veh_avg"].copy()
                esti_data["target"] = target_category(esti_data,ref)
                esti_data.to_csv("defense/out"+str(i)+"/"+lane+".csv" , index=False)
            except OSError as e:
                #print(e)
                pass
            except KeyError as e:
                #print(e)
                pass
                
    ED = datetime.datetime.now()

    time_series = ED-ST
    Tlog = "Time for executing defensewithSVM.py　=> " + str(time_series)+"\n"
    wf = open("Timer/timer.txt" , mode='a')    
    wf.write(Tlog)
    wf.close()

        
