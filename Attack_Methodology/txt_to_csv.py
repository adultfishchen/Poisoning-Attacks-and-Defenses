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
import datetime
import warnings

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
    print("Start tranfer files...")
    # All road_segs on each day use the same value with ADD algo.
    
    for i in range(start,end):
        if not os.path.exists('csv_result/out'+str(i)):
            os.makedirs('csv_result/out'+str(i))
        
        if not os.path.exists('tamperRecord_result/out'+str(i)):
            os.makedirs('tamperRecord_result/out'+str(i))
        # Extent of Tampering    
        tampered_ref = 1.0
        log = str(i)+" => Add:" + str(tampered_ref)
        
        wf = open("tamperRecord_result/out"+str(i)+"/tamper.txt" , mode='a')
        log += "\n"
        wf.write(log)
        wf.close()

        warnings.filterwarnings("ignore")
        for lane, lanelen in Lane_dict.items():
            data = pd.DataFrame(columns=["vehid","entry","mid","instspeed","exit","length"])
            lane_len = lanelen
            try:
                with open("txt_result/out"+str(i)+"/"+lane+".txt",'r') as rf:
                    for line in rf:
                        line.replace("\n", "")
                        if line != "":
                            token = line.split(",")
                            veh_id = token[0]
                            veh_entry = float(token[1])
                            veh_midentry = float(token[2])
                            veh_inst = float(token[3])
                            veh_exit = float(token[4])
                            if veh_entry <= veh_exit:
                                newrow = {"vehid":veh_id ,"entry":veh_entry ,"mid":veh_midentry ,"instspeed":veh_inst , "exit": veh_exit,"length":lane_len}
                            else:                              
                                newrow = {"vehid":veh_id ,"entry":veh_exit ,"mid":veh_midentry ,"instspeed":veh_inst ,"exit": veh_entry,"length":lane_len}
                            data = data.append(newrow, ignore_index=True)
                    #print(data["exit"])
                    
                    
                    data = data.sort_values(by=["exit"])
                    # Methods of Seleting Target Poisoned Data                    
                    # Random 
                    # Sample 20% data, and tamper instspeed by adding tampered_ref[0]
                    f_data_Add = data.sample(frac=0.2)
                    
                    # Drop these rows from the origin dataframe
                    d_ref_a=f_data_Add.exit
                    data = data[~data['exit'].isin(d_ref_a)]
                    
                    for j in range(len(f_data_Add)):
                      # Setting Attacking Algorithm 
                      temp = f_data_Add.iloc[j]["instspeed"]+tampered_ref
                      
                      # Data Rolling Back Mechanism
                      if temp > 18.0:
                        temp = 16.0
                        f_data_Add["instspeed"] = f_data_Add["instspeed"].replace(f_data_Add.iloc[j]["instspeed"],temp)
                        
                      elif temp < 3.0:
                        temp = 5.0
                        f_data_Add["instspeed"] = f_data_Add["instspeed"].replace(f_data_Add.iloc[j]["instspeed"],temp)
                        
                      else: 
                        f_data_Add["instspeed"] = f_data_Add["instspeed"].replace(f_data_Add.iloc[j]["instspeed"],temp)
                        
                        
                    
                    # Tamper Exit Time (plus)
                    for j in range(len(f_data_Add)):
                      temp = f_data_Add.iloc[j]["exit"] + 30.0
                      
                      f_data_Add["exit"] = f_data_Add["exit"].replace(f_data_Add.iloc[j]["exit"],temp)
                    
                    mixed = pd.concat([data,f_data_Add],axis=0).drop_duplicates(subset=['vehid']).sort_index()
                   
                    '''
                    #Fast
                    sorted_data = data.sort_values(by=["instspeed"], ascending = False)
                    # Retrieve top 20% data as tampered datasets
                    fast_data = sorted_data.iloc[:int(len(data)/5)]
                    # Drop these rows from the origin dataframe
                    fast_ref=fast_data.exit
                    data = data[~data['exit'].isin(fast_ref)]
                    # Tamper instspeed by adding tampered_ref[0]
                    f_data_Add = fast_data
                    
                    
                    for j in range(len(f_data_Add)):
                      temp = f_data_Add.iloc[j]["instspeed"]+tampered_ref
                      if temp > 18.0:
                        temp = 16.0
                        f_data_Add["instspeed"] = f_data_Add["instspeed"].replace(f_data_Add.iloc[j]["instspeed"],temp)                        
                        
                      elif temp < 3.0:
                        temp = 5.0
                        f_data_Add["instspeed"] = f_data_Add["instspeed"].replace(f_data_Add.iloc[j]["instspeed"],temp)                        
                       
                      else: 
                        f_data_Add["instspeed"] = f_data_Add["instspeed"].replace(f_data_Add.iloc[j]["instspeed"],temp)
                        
                       
                    
                    # Tamper Exit Time (plus)
                    for j in range(len(f_data_Add)):
                      temp = f_data_Add.iloc[j]["exit"] + 30.0
                      
                      f_data_Add["exit"] = f_data_Add["exit"].replace(f_data_Add.iloc[j]["exit"],temp)
                    
                   
                    # Concate the data, which will contain 20% tampered data
                    mixed = pd.concat([data,f_data_Add],axis=0).drop_duplicates(subset=['vehid']).sort_index()
                    
                    '''
                    
                    '''
                    # Slow
                    sorted_data =data.sort_values(by=["instspeed"], ascending = True)
                    # Retrieve bottom 20% data as tampered datasets
                    slow_data = sorted_data.iloc[:int(len(data)/5)]
                    # Drop these rows from the origin dataframe
                    slow_ref=slow_data.exit
                    data = data[~data['exit'].isin(slow_ref)]
                    # Tamper instspeed by adding tampered_ref[0]
                    f_data_Add = slow_data
                    
                    for j in range(len(f_data_Add)):
                      temp = f_data_Add.iloc[j]["instspeed"]+tampered_ref
                      if temp > 18.0:
                        temp = 16.0
                        f_data_Add["instspeed"] = f_data_Add["instspeed"].replace(f_data_Add.iloc[j]["instspeed"],temp)
                        #print("f = ",f_data_Add.iloc[j]["instspeed"])
                        
                      elif temp < 3.0:
                        temp = 5.0
                        f_data_Add["instspeed"] = f_data_Add["instspeed"].replace(f_data_Add.iloc[j]["instspeed"],temp)
                        
                        #print("Temp = "+str(temp)+", f = "+str(f_data_Add.iloc[j]["instspeed"]))
                      else: 
                        f_data_Add["instspeed"] = f_data_Add["instspeed"].replace(f_data_Add.iloc[j]["instspeed"],temp)
                        
                        #print("Temp = "+str(temp)+", f = "+str(f_data_Add.iloc[j]["instspeed"]))
                    
                    # Tamper Exit Time (Plus)
                    for j in range(len(f_data_Add)):
                      temp = f_data_Add.iloc[j]["exit"] + 30.0
                      
                      f_data_Add["exit"] = f_data_Add["exit"].replace(f_data_Add.iloc[j]["exit"],temp)
                    
                   
                    mixed = pd.concat([data,f_data_Add],axis=0).drop_duplicates(subset=['vehid']).sort_index()
                    
                   
                    '''
                    mixed.to_csv('csv_result/out'+str(i)+"/"+lane +".csv" , index=False)
                      
            except Exception as e:
                #print(e)
                continue

    ED = datetime.datetime.now()

    time_series = ED-ST
    Tlog = "Time for executing txt_to_csv.py => " + str(time_series)+"\n"
    wf = open("Timer/timer.txt" , mode='a')    
    wf.write(Tlog)
    wf.close()