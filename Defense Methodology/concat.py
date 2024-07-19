from __future__ import absolute_import
from __future__ import print_function
import xml.etree.cElementTree as ET
import numpy as np
import pandas as pd
import csv
import os
import sys
import warnings
import optparse
from optparse import OptionParser
import datetime

if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import sumolib

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
    print("Concat begin......")
    for i in range(start,end):
      if not os.path.exists('concat/out'+str(i)):
            os.makedirs('concat/out'+str(i))
    
      #for lane in lane_list:
      for lane, lanelen in Lane_dict.items():
          try:
            tamper_data = pd.read_csv('csv_result/out'+str(i)+"/"+lane +".csv")
            real_data = pd.read_csv('real_csv_result/out'+str(i)+"/"+lane +".csv")
            tamper_data["real_instspeed"] = real_data["instspeed"]
            tamper_data["real_entry"] = real_data["entry"]
            tamper_data["real_exit"] = real_data["exit"]
            tamper_data.to_csv('concat/out'+str(i)+"/"+lane +".csv" , index=False)
          except OSError as e:
              #print(e)
              pass
    ED = datetime.datetime.now()

    time_series = ED-ST
    Tlog = "Time for executing concat.py　=> " + str(time_series)+"\n"
    wf = open("Timer/timer.txt" , mode='a')    
    wf.write(Tlog)
    wf.close()