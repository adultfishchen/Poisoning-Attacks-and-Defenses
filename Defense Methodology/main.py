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

# this is the main entry point of this script
if __name__ == "__main__":
    parser = OptionParser()#parser = OptionParser()
    parser.add_option("-s", "--start", dest="start",type="int" , default="-1", help="The start used to run SUMO start from tripinfox.xml")
    parser.add_option("-e", "--end", dest="end",type="int" , default="-1", help="The end used to run SUMO end at tripinfox.xml")
    (options, args) = parser.parse_args()
    start = options.start
    end = options.end
    
    if not os.path.exists('Timer'):
        os.makedirs('Timer')
    # The Worst Attack Situation
    
    os.system("python3 concat.py -s "+str(start)+" -e "+str(end))
    os.system("python3 defense.py -s "+str(start)+" -e "+str(end))
    os.system("python3 combine_defense.py -s "+str(start)+" -e "+str(end))
    os.system("python3 SVM.py")
    os.system("python3 Linear_Regression.py")
    os.system("python3 recover.py -s "+str(start)+" -e "+str(end))
    os.system("python3 vehavg_inst.py -s "+str(start)+" -e "+str(end))
    
    
    if start == 0:
        os.system("python3 finalavg.py")
        os.system("python3 train.py")
    '''
    # Similar Situation
    
    os.system("python3 defense_withSVM.py -s "+str(start)+" -e "+str(end))
    
    os.system("python3 recover_withSVM.py -s "+str(start)+" -e "+str(end))
    os.system("python3 vehavg_inst.py -s "+str(start)+" -e "+str(end))
    
    
    if start == 0:
        os.system("python3 finalavg.py")
        os.system("python3 train.py")
   ''' 