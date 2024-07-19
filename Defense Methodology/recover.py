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
    print("Recover start......")
    for i in range(start,end):
        if not os.path.exists('Sterilized/out'+str(i)):
            os.makedirs('Sterilized/out'+str(i))
        print("i= ",i)
    
        for lane in Lane_dict.keys():       
            try:
                data = pd.read_csv("defense/out"+str(i)+"/"+lane+".csv")
                ref = pd.read_csv("Reference/relationships_recover.csv")
                sv = ref.loc[ref['Lane'] == lane]['slope_v'].tolist()             
                interv = ref.loc[ref['Lane'] == lane]['intercept_v'].tolist()
                si = ref.loc[ref['Lane'] == lane]['slope_i'].tolist()
                interi = ref.loc[ref['Lane'] == lane]['intercept_i'].tolist()
                
                # Recover Veh_avg
                data.loc[data.target == 0, 'veh_avg'] = (float(sv[0])*data['tamper_vehavg'])+float(interv[0])
                # Recover exit
                data.loc[data.target == 0, 'exit'] = (data['length']/data['veh_avg'])+data['entry']
                # Recover instspeed
                data.loc[data.target == 0, 'instspeed'] = (float(si[0])*data['tamper_vehavg'])+float(interi[0])
                
                
                data = data.drop(["veh_avg","tamper_vehavg","target"], axis=1) 
                #data = data.drop(["real_entry","real_exit","real_instspeed","veh_avg","tamper_vehavg","target"], axis=1)
                data.to_csv("Sterilized/out"+str(i)+"/"+lane+".csv" , index=False)
                
            except OSError as e:
                #print(e)
                pass
            except ValueError as e:
                #print(e)
                pass
            except IndexError as e:
                #print(e)
                pass
            except KeyError as e:
                #print(e)
                pass

    ED = datetime.datetime.now()

    time_series = ED-ST
    Tlog = "Time for executing recover.py　=> " + str(time_series)+"\n"
    wf = open("Timer/timer.txt" , mode='a')    
    wf.write(Tlog)
    wf.close()