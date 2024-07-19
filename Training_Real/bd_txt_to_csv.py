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
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import sumolib





if __name__ == "__main__":
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
        if not os.path.exists('bd_csv_result/out'+str(i)):
            os.makedirs('bd_csv_result/out'+str(i))

        for lane, lanelen in Lane_dict.items():
            #data = pd.DataFrame(columns=["entry","mid","instspeed","exit","length"])
            data = pd.DataFrame(columns=["vehid","instspeed","Bd"])
            lane_len = lanelen
            try:
                with open("Bd/out"+str(i)+"/"+lane+".txt",'r') as rf:
                    for line in rf:
                        line.replace("\n", "")
                        if line != "":
                            token = line.split(",")
                            vid = float(token[0])                            
                            veh_inst = float(token[1])
                            veh_bd= float(token[2])
                            #real_exit = float(token[5])
                            
                            newrow = {"vehid":vid ,"instspeed":veh_inst , "Bd": veh_bd}
                        
                            data = data.append(newrow, ignore_index=True)
                    #print(data["exit"])
                    data = data.sort_values(by=["vehid"])
                    #print("enter")
                    #print(data["exit"])
                    data.to_csv('bd_csv_result/out'+str(i)+"/"+lane +".csv" , index=False)

            except:
                continue

