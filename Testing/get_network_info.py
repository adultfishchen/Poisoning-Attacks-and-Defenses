from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import optparse
import xml.etree.cElementTree as ET
import numpy as np
import pandas as pd
import networkx as nx

# we need to import python modules from the $SUMO_HOME/tools directory
if 'SUMO_HOME' in os.environ:
    tools = os.path.join(os.environ['SUMO_HOME'], 'tools')
    sys.path.append(tools)
else:
    sys.exit("please declare environment variable 'SUMO_HOME'")

from sumolib import checkBinary  # noqa
import sumolib
import traci  # noqa
from tensorflow.python.keras.models import load_model


def GetRoadModel():
    Mod_dir = 'data/models/'
    NetName = "data/01/Tainan.net.xml"
    net = sumolib.net.readNet(NetName)
    edges = net.getEdges()
    Model_dict = {}
    for edge in edges:
        #Model_dict[edge.getID()] = 0
        #'''
        try:
            model = load_model(Mod_dir+edge.getID()+"_model.h5") 
            Model_dict[edge.getID()] = model
        except:
            Model_dict[edge.getID()] = 0
            pass
        #'''

        

    return Model_dict

def GetMinMax(data_len):
    return max(data_len) , min(data_len)

def MakePdAndDict(data_max,data_min,columns):
    Index_list = []
    Num_dict = {}
    
    for i in range(data_min,data_max):
        Num_dict[i] = 0
        Index_list.append(i)

    df = pd.DataFrame(columns = columns, 
                   index = Index_list)
    df = df.fillna(0) 
    return df , Num_dict

def GetPastMeanZ():
    csvfile = 'data/meanZ/selected_'
    NetName = "data/01/Tainan.net.xml"
    net = sumolib.net.readNet(NetName)
    edges = net.getEdges()
    MeanZ_dict = {}
    #edges = [net.getEdge("-160253722#7")]
    for edge in edges:
        lanes = edge.getLanes()
        total = 0
        flag = 0
        sel_len = []

        for idx , lane in enumerate(lanes):
            try:
                tempSelected_data = pd.read_csv(csvfile+lane.getID()+"_mean.csv")
                tempSelected_data = tempSelected_data.drop(columns="interval")
                tempSelected_data = tempSelected_data.drop(columns="SelectedNum")
                sel_len.append(len(tempSelected_data))
            except:
                continue
        if not sel_len:
            MeanZ_dict[edge.getID()] = {}
            MeanZ_dict[edge.getID()]["Zmax"] = []
            MeanZ_dict[edge.getID()]["Zmin"] = []
            MeanZ_dict[edge.getID()]["q_value"] = []
            continue
        sel_max , sel_min = GetMinMax(sel_len)
        columns = tempSelected_data.columns.values.tolist()
        sel_total_df , sel_num_dict = MakePdAndDict(sel_max,sel_min,columns)


        for idx , lane in enumerate(lanes):
            try:
                tempSelected_data = pd.read_csv(csvfile+lane.getID()+"_mean.csv")
                tempSelected_data = tempSelected_data.drop(columns="interval")
                tempSelected_data = tempSelected_data.drop(columns="SelectedNum")
            except Exception as e:
                #print(e)
                pass

            if flag == 0:
                    if len(tempSelected_data) >= sel_min:
                        mean = tempSelected_data[:sel_min]

                    for i in range(sel_min,len(tempSelected_data) ):
                        sel_total_df.loc[i] += tempSelected_data.iloc[i]
                        sel_num_dict[i] += 1
                    total += 1
                    flag = 1

            else:
                    if len(tempSelected_data) >= sel_min:
                        mean += tempSelected_data[:sel_min]

                    for i in range(sel_min,len(tempSelected_data) ):
                        sel_total_df.loc[i] += tempSelected_data.iloc[i]
                        sel_num_dict[i] += 1
                    total += 1
            
        if total == 0:
            MeanZ_dict[edge.getID()] = {}
            MeanZ_dict[edge.getID()]["Zmax"] = []
            MeanZ_dict[edge.getID()]["Zmin"] = []
            MeanZ_dict[edge.getID()]["q_value"] = []
        else:
            mean /= total
            for i in range(sel_min,sel_max):
                sel_total_df.loc[i] /=sel_num_dict[i]
                mean = mean.append(sel_total_df.loc[i])

            MeanZ_dict[edge.getID()] = {}
            MeanZ_dict[edge.getID()]["Zmax"] = mean["Zmax"].tolist()
            MeanZ_dict[edge.getID()]["Zmin"] = mean["Zmin"].tolist()
            MeanZ_dict[edge.getID()]["q_value"] = mean["q_value"].tolist()

    return MeanZ_dict

def GetPastMeanSpeed():
    csvfile = 'data/mean/'
    NetName = "data/01/Tainan.net.xml"
    net = sumolib.net.readNet(NetName)
    edges = net.getEdges()
    MeanSpeed_dict = {}
    for edge in edges:
        lanes = edge.getLanes()
        total = 0
        flag = 0
        for idx , lane in enumerate(lanes):
            try:
                if flag == 0:
                    mean = pd.read_csv(csvfile+lane.getID()+"_mean.csv")
                    mean = mean.drop(columns="interval")
                    mean = mean.drop(columns="avgspeed")
                    flag = 1
                    total +=1

                else:
                    temp = pd.read_csv(csvfile+lane.getID()+"_mean.csv")
                    temp = temp.drop(columns="interval")
                    temp = temp.drop(columns="avgspeed")
                    
                    if len(mean) >= len(temp):
                        mean += temp.reindex_like(mean).fillna(13.89)
                    else:
                        mean = mean.reindex_like(temp).fillna(13.89) + temp
                        
                    total +=1
            except Exception as e:
                #print(e)
                pass
        if total == 0:
            MeanSpeed_dict[edge.getID()] = []
        else:           
            mean /= total
            MeanSpeed_dict[edge.getID()] = mean["instspeed"].tolist()

        

    return MeanSpeed_dict

"""get the info of road segments from <net.xml>"""
def getRNinfo():

    tree = ET.ElementTree(file='data/Tainan.net.xml')
    tree.getroot()
    
    """
    RoadSegment_info
    {id:[from(node),to(node),lenght,lane_number]
    """
    RS_info = {}
              
    for elem in tree.iter(tag='edge'):
        
        """sieve out internal edge"""
        if elem.attrib['id'].find(':') == -1:
            
            lanelist = []
            lanename = []
            for lane in elem.iter(tag='lane'):
                lanelist.append(float(lane.attrib['length']))
                lanename.append(lane.attrib['id'])
                
            RS_info.update({elem.attrib['id']:[elem.attrib['from'],elem.attrib['to'],str(np.mean(lanelist)),str(len(lanelist)),lanename[0]]})            
            
    """
    connection_info
    (from, to)
    """
    con_info = []
    
    for elem in tree.iter(tag='connection'):
        if (elem.attrib['from'].find(':') == -1) and (elem.attrib['to'].find(':') == -1):
            con_info.append((elem.attrib['from'],elem.attrib['to']))
    
    """
    TL_info:
    {TL_id:[[duration,state] for all phase]}
    """    
    TL_info = {}
    
    for TL in tree.iter(tag='tlLogic'):
        TL_info[TL.attrib['id']] = []
        for elem in TL.iter(tag='phase'):
            TL_info[TL.attrib['id']].append([elem.attrib['duration'], elem.attrib['state']])
            
    """
    conn_TL:
    {(from_edge,to_edge):[TL_id,index]}
    """   
    conn_TL = {}
         
    for elem in tree.iter(tag='connection'):
        if (elem.attrib['from'].find(':') == -1) and (elem.attrib['to'].find(':') == -1):
            if 'tl' in elem.attrib: 
                conn_TL[(elem.attrib['from'],elem.attrib['to'])] = [elem.attrib['tl'], elem.attrib['linkIndex']]
            else:
                conn_TL[(elem.attrib['from'],elem.attrib['to'])] = []
    return RS_info, con_info, TL_info, conn_TL



"""load Road Network from <net.xml>"""
def loadedgeRN(RS_info, con_info):
    RSLen_list = []
    for data in RS_info.values():
        RSLen_list.append(float(data[2]))

    Max_len = max(RSLen_list)    
    Min_len = min(RSLen_list)
    if np.mean(RSLen_list) == 0:
        CV_len = 0
    else:
        CV_len = np.std(RSLen_list)/np.mean(RSLen_list)
    
    RN = nx.DiGraph()
    
    for conn in con_info:
        
        """"weight = 0 , length = Normalization of length , len_CV """
        #print(conn[0])
        #print(type(RS_info))
        #print(RS_info[conn[0]])
        #print(RS_info[conn[0]][2])
        
        Normalize_len = (float(RS_info[conn[0]][2]) - Min_len ) / (Max_len - Min_len)
        #print(Normalize_len)
        RN.add_edge(conn[0], conn[1], weight = 0 , length = Normalize_len , len_CV=CV_len)
        
    return RN

"""get node's Coordinate from node file"""
def getCoordinate():

    tree = ET.ElementTree(file='data/plain.nod.xml')
    tree.getroot()
    
    """
    Coordinate
    0:id;
    1:x;
    2:y
    """
    
    Coordinate = {}
    i = 0
    for elem in tree.iter(tag='node'):
        
        """{node_id:[x, y]}"""
        Coordinate.update({elem.attrib['id']:[float(elem.attrib['x']), float(elem.attrib['y'])]})            
        i += 1

    return Coordinate