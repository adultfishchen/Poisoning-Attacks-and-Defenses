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
    for i in range(start,end):
        if not os.path.exists('csv_result/out'+str(i)):
            os.makedirs('csv_result/out'+str(i))

        for lane, lanelen in Lane_dict.items():
            #data = pd.DataFrame(columns=["entry","mid","instspeed","exit","length"])
            data = pd.DataFrame(columns=["vehid","entry","mid","instspeed","exit","length"])
            lane_len = lanelen
            try:
                with open("txt_result/out"+str(i)+"/"+lane+".txt",'r') as rf:
                    for line in rf:
                        line.replace("\n", "")
                        if line != "":
                            token = line.split(",")
                            vid = float(token[0])
                            veh_entry = float(token[1])
                            veh_midentry = float(token[2])
                            veh_inst = float(token[3])
                            veh_exit = float(token[4])
                            #real_exit = float(token[5])
                            if veh_entry <= veh_exit:
                              newrow = {"vehid":vid ,"entry":veh_entry ,"mid":veh_midentry ,"instspeed":veh_inst , "exit": veh_exit,"length":lane_len}
                            else:
                              
                              newrow = {"vehid":vid ,"entry":veh_exit ,"mid":veh_midentry ,"instspeed":veh_inst ,"exit": veh_entry,"length":lane_len}
                            data = data.append(newrow, ignore_index=True)
                    #print(data["exit"])
                    data = data.sort_values(by=["exit"])
                    #print("enter")
                    #print(data["exit"])
                    data.to_csv('csv_result/out'+str(i)+"/"+lane +".csv" , index=False)

            except:
                continue

    ED = datetime.datetime.now()

    time_series = ED-ST
    Tlog = "Time for executing txt_to_csv.py　=> " + str(time_series)+"\n"
    wf = open("Timer/timer.txt" , mode='a')    
    wf.write(Tlog)
    wf.close()  