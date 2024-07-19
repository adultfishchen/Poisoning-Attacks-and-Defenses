from __future__ import absolute_import
from __future__ import print_function
import xml.etree.cElementTree as ET
import numpy as np
import pandas as pd
import optparse
from optparse import OptionParser
import csv
import os
import sys
import math
import fnmatch
import warnings
import statistics as st
from glob import glob
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
    print("Combine_csv begin......")
    
    for lane in Lane_dict.keys():
      if not os.path.exists('SVM_ref/'):
              os.makedirs('SVM_ref/')
        
      try:
          for i in range(start,end):
              # 設定主資料夾路徑
              main_folder = 'defense/'
  
              # 找到所有符合條件的CSV檔案路徑
              file_paths = []
              for root, dirs, files in os.walk(main_folder):
                  for dir in dirs:
                      if dir.startswith("out"):
                          dir_path = os.path.join(root, dir)
                          file_path = os.path.join(dir_path, f"{lane}.csv")
                          if os.path.exists(file_path):
                              file_paths.append(file_path)
  
              # 讀取所有CSV檔案並合併成一個DataFrame
              dfs = [pd.read_csv(file_path) for file_path in file_paths]
              merged_df = pd.concat(dfs,axis=0)
  
              # 將結果寫入到新的CSV檔案中
              merged_df.to_csv("SVM_ref/"+lane+".csv", index=False)
      except OSError as e:
          #print(e)
          pass
      except ValueError:
          pass
          
    ED = datetime.datetime.now()

    time_series = ED-ST
    Tlog = "Time for executing combine_defense.py　=> " + str(time_series)+"\n"
    wf = open("Timer/timer.txt" , mode='a')    
    wf.write(Tlog)
    wf.close()