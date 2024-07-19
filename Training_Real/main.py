from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import optparse
from optparse import OptionParser
#import random
import time
#import networkx as nx
import numpy as np
#from numpy import ndarray
import gc
import get_network_info as gni
#import traffic_congestion_prediction as tcp
#import vehicle_selection as vs
#import vehicle_rank as vr
#import reroute_algorithm as ra
import xml.etree.cElementTree as ET
#from tensorflow.python.keras.models import load_model
#import json
from interval import Interval

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

def GetStart(Lane_dict):
    for laneid in Lane_dict.keys():
      
      global time_e
      
      loopid ="Start_"+laneid
      info = traci.inductionloop.getVehicleData(loopid)

      if  info : # not empty list
          if -1 == info[0][3]:
              continue
          veh_id = info[0][0]
          veh_entry = info[0][2]
          if veh_id not in Lane_dict[laneid]:
              Lane_dict[laneid][veh_id] = {}
              #log += "Evehid Create"+"\n"
              #print("Evehid Create")          
          
          vehID = veh_id
          s = traci.vehicle.getSpeed(vehID)
          #a = traci.vehicle.getAcceleration(vehID)
          #ms = traci.vehicle.getMaxSpeed(vehID)
          #wt = traci.vehicle.getWaitingTime(vehID)
          
          if s == 0.0:
              time_e = traci.simulation.getTime()
              Lane_dict[laneid][veh_id]["veh_entry"] = time_e
          elif "veh_entry" not in Lane_dict[laneid][veh_id]:
              Lane_dict[laneid][veh_id]["veh_entry"] = veh_entry

          
    return Lane_dict
    
def GetMid(Lane_dict,outer_i):
    for laneid in Lane_dict.keys():
    
      global time_e
      loopid ="Mid_"+laneid
      info = traci.inductionloop.getVehicleData(loopid)
      
      
      if  info : # not empty list
          if -1 == info[0][3]:
              continue
          veh_id = info[0][0]
          veh_entry = info[0][2]
           
          if veh_id not in Lane_dict[laneid]:
              #print("Mvehid")
              #Lane_dict[laneid][veh_id] = {}
              continue
              
          instspeed = traci.inductionloop.getLastStepMeanSpeed(loopid)
          if instspeed == -1:
              continue
          
          vehID = veh_id
          
          
          s = traci.vehicle.getSpeed(vehID)
          Bd = st.norm.cdf(traci.vehicle.getSpeedFactor(vehID), loc = 0.95, scale = 0.1)
          
          wf = open("Bd/out"+str(outer_i)+"/"+laneid+".txt" , mode='a')    
          line = vehID+","+str(instspeed)+","+ str(Bd) +"\n"
          #print("L=",line)
          wf.write(line)
          wf.close()
          #a = traci.vehicle.getAcceleration(vehID)
          #ms = traci.vehicle.getMaxSpeed(vehID)
          #wt = traci.vehicle.getWaitingTime(vehID)
          #if s <= 1.0 and Lane_dict[laneid][veh_id]["veh_e"] == 0.0:
          if s == 0.0:
              time_e = traci.simulation.getTime()
              Lane_dict[laneid][veh_id]["veh_midentry"] = veh_entry
              #print("VheID = "+str(veh_id)+"MidEntry = "+str(Lane_dict[laneid][veh_id]["veh_midentry"]))
              Lane_dict[laneid][veh_id]["veh_mid"] = instspeed
              Lane_dict[laneid][veh_id]["veh_entry"] = time_e
              #print("End of Stop"+str(time_e))        
          
          else:
              Lane_dict[laneid][veh_id]["veh_midentry"] = veh_entry
              #print("VheID = "+str(veh_id)+"MidEntry = "+str(Lane_dict[laneid][veh_id]["veh_midentry"]))
              Lane_dict[laneid][veh_id]["veh_mid"] = instspeed
          
          #print("VheID = "+str(veh_id)+"veh_e = "+str(Lane_dict[laneid][veh_id]["veh_e"]))
          
    return Lane_dict

def GetEnd(Lane_dict):
    for laneid in Lane_dict.keys():
    
      global time_e
      loopid ="End_"+laneid
      info = traci.inductionloop.getVehicleData(loopid)
      
      
      if  info : # not empty list
          if -1 == info[0][3]:
              continue
          veh_id = info[0][0]
          veh_exit = info[0][2]
          if veh_id not in Lane_dict[laneid]:
              Lane_dict[laneid][veh_id] = {}
              #log += "Evehid Create"+"\n"
              #print("Evehid Create")          
          
          vehID = veh_id
          s = traci.vehicle.getSpeed(vehID)
          #a = traci.vehicle.getAcceleration(vehID)
          #ms = traci.vehicle.getMaxSpeed(vehID)
          #wt = traci.vehicle.getWaitingTime(vehID)
          
          if s == 0.0 and "veh_exit" not in Lane_dict[laneid][veh_id]:
              time_e = traci.simulation.getTime()
              Lane_dict[laneid][veh_id]["veh_exit"] = time_e
              #print("End of Stop"+str(time_e))
          elif s == 0.0 and "veh_exit" in Lane_dict[laneid][veh_id]:
              continue
          else:
              Lane_dict[laneid][veh_id]["veh_exit"] = veh_exit

          #print("VheID = "+str(veh_id)+" ,LandID = " + str(laneid) +" ,exit = "+str(veh_exit)+" ,veh_E = "+str(Lane_dict[laneid][veh_id]["veh_exit"]))
    return Lane_dict
 
    
def initialize():
    NetName = "data/01/Tainan.net.xml"
    net = sumolib.net.readNet(NetName)
    edges = net.getEdges()
    Lane_dict = {}
    for edge in edges:
        lanes = edge.getLanes()
        for lane in lanes:
            Lane_dict[lane.getID()] = {}

    alledgelist = traci.edge.getIDList()
    speed_info = {}
    speed_result = {}
    edgeocc_dict = {}
    oneminspeed_dict = {}
    for EdgeID in alledgelist:
        
        if EdgeID.find(':') == -1:
            speed_info[EdgeID] = []
            oneminspeed_dict[EdgeID] = []
            speed_result[EdgeID] = []
            edgeocc_dict[EdgeID] = {}



    tree = ET.ElementTree(file='data/RSUsLocationUBC.xml')
    tree.getroot()

    Zone_dict = {}
    Zoneidx = 0
    AllEdge_list = []
    EdgeTOZone_dict = {}
    for elem in tree.iter(tag='poly'):
        x , y = elem.attrib['center'].split(",")
        edges = net.getNeighboringEdges(float(x), float(y), 330)#330
        ZoneEdge_list = []
        for edge in edges:
            closestEdge , distance = edge
            #print(closestEdge)
            EdgeID = str(closestEdge).split('id=')[1].split(' ')[0].replace('"',"")  
            #if EdgeID == "319713269#2":
            #    print("Yes")
            #print(EdgeID)
            if EdgeID in AllEdge_list:
                continue
            EdgeTOZone_dict[EdgeID] = Zoneidx
            AllEdge_list.append(EdgeID)
            
            ZoneEdge_list.append(EdgeID)

        Zone_dict[Zoneidx] = ZoneEdge_list
        
        Zoneidx += 1


        

    return Lane_dict , speed_info , oneminspeed_dict , speed_result , edgeocc_dict , Zone_dict ,EdgeTOZone_dict



def run(i,VR):
    total_diff = 0
    total_same = 0
    #log = ""
    #s = 0
    step = 0
    
    Lane_dict , speed_info , oneminspeed_dict , speed_result , edgeocc_dict , Zone_dict , EdgeTOZone_dict = initialize()

    """get road network info."""    
    RS_info, con_info, TL_info, conn_TL = gni.getRNinfo()
    RN = gni.loadedgeRN(RS_info, con_info)
    Coordinate = gni.getCoordinate()
    if not os.path.exists('Bd/out'+str(i)):
        os.makedirs('Bd/out'+str(i))
    while traci.simulation.getMinExpectedNumber() > 0:
        traci.simulationStep()

        
        """collect road speed and output in txt_result/"""
        try:
            
            Lane_dict = GetStart(Lane_dict)
            Lane_dict = GetMid(Lane_dict,i)
            Lane_dict = GetEnd(Lane_dict)
            #print(Lane_dict)

        except traci.TraCIException:
            pass
        except Exception:
            pass
        

        SimTime = int(traci.simulation.getTime())
        
        #if SimTime > 400:
        #    break
        """get speed info: do every 10 sec. (time step)"""
        if SimTime  % 10 == 0:
            for EdgeID, speed_list in speed_info.items():
                speed_list.append(traci.edge.getLastStepMeanSpeed(EdgeID))
                
        if SimTime %60==0:
            
            """ update speed data per min."""
            for EdgeID, speed_list in speed_info.items():
                temp_list = speed_list
                tempAvgSpeed = np.mean(temp_list)
                oneminspeed_dict[EdgeID].append(tempAvgSpeed)
                speed_list[:] = []

        if SimTime %300 == 0:
        
            for EdgeID, speed_list in oneminspeed_dict.items():
                if len(speed_list) !=5:
                    print("speed list !=5")
                    exit(0)
                temp_list = speed_list
                tempAvgSpeed = np.mean(temp_list)
                speed_result[EdgeID] = tempAvgSpeed
                speed_list[:] = []
            
            
        
        
        step += 1 
        #s += 1
    
    traci.close()
    sys.stdout.flush()
    '''
    if not os.path.exists('log_result/'):
        os.makedirs('log_result/')
    wf = open("log_result/log"+str(i)+".txt" , mode='w')    

    wf.write(log)
    wf.close()
    '''
    
    if not os.path.exists('txt_result/out'+str(i)):
        os.makedirs('txt_result/out'+str(i))
        
    for laneid in Lane_dict.keys():
        if len(Lane_dict[laneid]) == 0:
            continue
        wf = open("txt_result/out"+str(i)+"/"+laneid+".txt" , mode='w')    
        for veh_id in Lane_dict[laneid]:
            try:
              line = str(veh_id)+","+str(Lane_dict[laneid][veh_id]["veh_entry"])+","+ str(Lane_dict[laneid][veh_id]["veh_midentry"])+","+\
              str(Lane_dict[laneid][veh_id]["veh_mid"])+","+str(Lane_dict[laneid][veh_id]["veh_exit"])+"\n"
              
              wf.write(line)
            except Exception as e:
                continue
        wf.close()
       
    
    gc.collect()

# this is the main entry point of this script
if __name__ == "__main__":
    parser = OptionParser()#parser = OptionParser()
    parser.add_option("-s", "--start", dest="start",type="int" , default="-1", help="The start used to run SUMO start from tripinfox.xml")
    parser.add_option("-e", "--end", dest="end",type="int" , default="-1", help="The end used to run SUMO end at tripinfox.xml")
    parser.add_option("--nogui", action="store_true",default=False, help="run the commandline version of sumo")
    (options, args) = parser.parse_args()
    start = options.start
    end = options.end
    
    
    if options.nogui:
        sumoBinary = checkBinary('sumo')
    else:
        sumoBinary = checkBinary('sumo')
        
    con_threshold = 0.7 #congestion threshold value
    
                
    for i in range(start,end):
        if i < 9:
            pn = "data/01"+"/re0"+str(i+1)+".sumocfg"
            fn = "Experiment_result/tripinfo0"+str(i+1)+".xml"
        else:
            pn = "data/01"+"/re"+str(i+1)+".sumocfg"
            fn = "Experiment_result/tripinfo"+str(i+1)+".xml"
        
        print(i+1,"begin at:",time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))  
        log = "Day "+ str(i+1) +"=> begin at:"+ str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())) 
        traci.start([sumoBinary, "-c", pn,"--tripinfo-output", fn])
        run(i,"ld")
        log += " => finish at:"+str(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        print(" finish at:",time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        
        if not os.path.exists('Time_result/'):
          os.makedirs('Time_result/')
        
        wf = open("Time_result/"+"record.txt" , mode='a')
        try:
          #print("Strat write")
          log += "\n"
          wf.write(log)
        except Exception as e:
          #print(e)
          continue
        wf.close() 
        gc.collect()
    gc.collect()
    
    os.system("python3 txt_to_csv.py -s "+str(start)+" -e "+str(end))
    
    os.system("python3 bd_txt_to_csv.py -s "+str(start)+" -e "+str(end))
    os.system("python3 vehavg_inst.py -s "+str(start)+" -e "+str(end))
    
    if start == 0:
        os.system("python3 finalavg.py")
        os.system("python3 train.py")
    
   