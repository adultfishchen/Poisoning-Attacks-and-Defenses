import xml.etree.cElementTree as ET
import numpy as np
import networkx as nx

"""get the info of road segments from <net.xml>"""
def getRNinfo():

    tree = ET.ElementTree(file='data/Tainan.net.xml')
    tree.getroot()
    
    """
    RoadSegment_info
    {id:[from(node),to(node),lengh,lane_number]
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

    # data = id
    for data in RS_info.values():
        
        #store "length" into list, detector info
        RSLen_list.append(float(data[2]))

    Max_len = max(RSLen_list)    
    Min_len = min(RSLen_list)
    
    if np.mean(RSLen_list) == 0:
        CV_len = 0
    else:
        # standard deviation / mean
        CV_len = np.std(RSLen_list)/np.mean(RSLen_list)
    
    RN = nx.DiGraph()
    
    for conn in con_info:
        
        """"weight = 0 , length = Normalization of length , len_CV is not used in the experiment """
        #print(conn[0])
        #print(type(RS_info))
        #print(RS_info[conn[0]])
        #print(RS_info[conn[0]][2])
        
        ## Normalization
        # (length- min) / (max-min)
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
    
    