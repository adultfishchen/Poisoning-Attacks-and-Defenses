from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import optparse
from optparse import OptionParser
#import random
import time
import datetime
#import networkx as nx
import numpy as np
import pandas as pd
#from numpy import ndarray
import gc
import get_network_info as gni
#import traffic_congestion_prediction as tcp
#import vehicle_selection as vs
#import vehicle_rank as vr
#import reroute_algorithm as ra
import xml.etree.cElementTree as ET
import math
from interval import Interval
#from tensorflow.python.keras.models import load_model
#import json
import warnings

RSNumber = 561
#rerouting_vehicle = {}

K = 7    #KSP
#con_threshold = 0.7 #congestion threshold value
#upstream_level = 3  #for selecting vehicles

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
  tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
  sys.path.append(tools)
else:
  sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import sumolib
import traci  # noqa
import scipy.stats as st




# this is the main entry point of this script
if __name__ == "__main__":

    ST = datetime.datetime.now()
    
    parser = OptionParser()#parser = OptionParser()
    parser.add_option("-s", "--start", dest="start",type="int" , default="-1", help="The start used to run SUMO start from tripinfox.xml")
    parser.add_option("-e", "--end", dest="end",type="int" , default="-1", help="The end used to run SUMO end at tripinfox.xml")
    
    (options, args) = parser.parse_args()
    start = options.start
    end = options.end
    
    NetName = "data/01/Tainan.net.xml"
    net = sumolib.net.readNet(NetName)
    edges = net.getEdges()
    Lane_list = []
    
    for edge in edges:
      lanes = edge.getLanes()
      for lane in lanes:
          Lane_list.append(lane.getID())
          
          
    con_threshold = 0.7 #congestion threshold value
    """get history average speed"""
    MeanSpeed_dict = gni.GetPastMeanSpeed()
    """get history Zmax Zmin"""
    MeanZ_dict = gni.GetPastMeanZ()
    """get model for all road"""
    Model_dict = gni.GetRoadModel()
    

    #Speed_dict = {}
    
    #os.system("python3 vehavg_inst.py -s "+str(start)+" -e "+str(end))
    lane_list = ["-496253687#1_0","250710099#0_0","-24452786#6_0","-160253722#7_0","-24452786#2_0","71285598#5_0","108037210#0_0","-496332201#4_0","-286094870#6_0","-227913938#10_0","307096544#4_0"]
    err = []   
    for i in range(start,end):
      err = [0] * 100
     
      print("i= ",i)
      if not os.path.exists('driver/out'+str(i)):
        os.makedirs('driver/out'+str(i))
       
      if not os.path.exists('log/out'+str(i)):
        os.makedirs('log/out'+str(i))
      
      if not os.path.exists('Timer'):
        os.makedirs('Timer')
      
      warnings.filterwarnings("ignore")
      #for lane in Lane_list:
      for lane in lane_list:   
          try:
              data = pd.read_csv("csv_result/out"+str(i)+"/"+lane+".csv")
              bd_data = pd.read_csv("bd_csv_result/out"+str(i)+"/"+lane+".csv")
              ins_data = pd.read_csv("interavg_result/out"+str(i)+"/"+lane+".csv")

              for idx in range(len(data)):
                      
                  RS = lane.split("_")[0]

                  MeanZ = MeanZ_dict[RS]

                  vehicle = data.iloc[idx]["vehid"]

                  vidx = bd_data.index[bd_data["vehid"]==vehicle].tolist()
                      
                  Bd = bd_data.at[vidx[0],"Bd"]
                      
                  model=Model_dict[RS]
                     
                  current_time = data.iloc[idx]["exit"]                      
                      
                  lastidx = int(current_time/300)
                  instspeed = ins_data.at[lastidx,"instspeed"]
                      
                  err[lastidx] = instspeed - MeanSpeed_dict[RS][lastidx]
                      
                  if lastidx == 0:
                      X = [[[0],[0],[0]]]        
                  elif lastidx == 1:
                      X = [[[0],[0],[err[lastidx-1]]]]
                  elif lastidx == 2:    
                      X = [[[0],[err[lastidx-2]],[err[lastidx-1]]]]
                  else :
                      X = [[[err[lastidx-3]],[err[lastidx-2]],[err[lastidx-1]]]]
                      
                      
                      
                  error = model.predict(np.array(X))
                  log =str(vehicle)+","+str(lastidx)+"," +str(MeanSpeed_dict[RS][lastidx]) +","+str(err[lastidx])+","+str(error)+"\n"
                 
                      
                  pred_inst = MeanSpeed_dict[RS][lastidx] + error
                  pred_avg = pred_inst *  ( (MeanZ["Zmax"][lastidx] - MeanZ["Zmin"][lastidx]) * math.pow(Bd, MeanZ["q_value"][lastidx]) + MeanZ["Zmin"][lastidx])
                 
                  wf = open("driver/out"+str(i)+"/"+lane+".txt" , mode='a')    
                  line = str(current_time) +","+str(vehicle)+","+str(RS)+","+str(pred_inst)+","+ str(Bd) +","+str(pred_avg) +"\n"
                  
                  wf.write(line)
                  wf.close()
                      
                      
                  wf = open('log/out'+str(i)+"/"+lane+"_mean_error.txt" , mode='a')    
                  wf.write(log)
                  wf.close()
                      
              
          except Exception as e:
              #print(e)
              continue
          
    ED = datetime.datetime.now()

    time_series = ED-ST
    Tlog = "Time for executing driver.py　=> " + str(time_series)          
    wf = open("Timer/timer.txt" , mode='a')    
    wf.write(Tlog)
    wf.close()