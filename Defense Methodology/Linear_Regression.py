from __future__ import absolute_import
from __future__ import print_function
import xml.etree.cElementTree as ET
import numpy as np
import pandas as pd
import csv
import matplotlib.pyplot as plt
import seaborn as sns
import statsmodels.api as sm
from matplotlib.pyplot import MultipleLocator
from scipy.interpolate import make_interp_spline
import os
import sys
import math
import fnmatch
import warnings
import statistics as st
from sklearn import svm
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
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
        
    NetName = "data/01/Tainan.net.xml"
    net = sumolib.net.readNet(NetName)
    edges = net.getEdges()
    Lane_dict = {}
    
    for edge in edges:
        lanes = edge.getLanes()
        for lane in lanes:
            Lane_dict[lane.getID()] = lane.getLength()
    
    
    
    with open("Reference/relationships_recover.csv", "w", newline='') as fp:    
        d = csv.writer(fp)
        d.writerow(["Lane","intercept_v","slope_v","intercept_i","slope_i"])
    warnings.filterwarnings("ignore")
    
    for lane in Lane_dict.keys():
        
      try:
         
          # Load Data
          data = pd.read_csv("SVM_ref/"+lane+".csv")
          subset = data[data['target'] == 0]
          
          subset.replace([np.nan,np.inf, -np.inf],0,inplace = True)
          
          ### Plot Linear Regression pic as Reference to recover exit time
          # Find out relationship of x and y
          x = subset['tamper_vehavg']
          y = subset['veh_avg']
  
          # Calculate Coefficient and regression parameter
          corr = np.corrcoef(x, y)[0, 1]
          model = sm.OLS(y, sm.add_constant(x)).fit()
          intercept_v, slope_v = model.params
          
          # Plot pic and Regression Line
          sns.regplot(x=x, y=y, line_kws={"color": "red"})
          plt.title(f'veh_avg = {slope_v:.3f}*tamper_vehavg + {intercept_v:.3f}')
          plt.xlabel('vehavg$_p$')
          plt.ylabel('vehavg$_r$')
          plt.savefig("Reference/"+lane+"_vehavgs.png")
          # Clear
          plt.clf()
  
          ### Plot Linear Regression pic as Reference to recover Instantaneous Speed
          # Retreive required data
          x = subset['tamper_vehavg']
          y = subset['real_instspeed']
  
          # Calculate Coefficient and regression parameter
          corr = np.corrcoef(x, y)[0, 1]
          model = sm.OLS(y, sm.add_constant(x)).fit()
          intercept_i, slope_i = model.params
          
          # Plot pic and Regression Line
          sns.regplot(x=x, y=y, line_kws={"color": "red"})
          plt.title(f'instspeed = {slope_i:.3f}*tamper_vehavg + {intercept_i:.3f}')
          plt.xlabel('vehavg$_p$')
          plt.ylabel('Instspeed$_r$')
          plt.savefig("Reference/"+lane+"_insts.png")
          # Clear
          plt.clf()
          
          # Records Parameters
          with open("Reference/relationships_recover.csv", "a", newline='') as fp:    
                  d = csv.writer(fp)
                  d.writerow([lane,intercept_v, slope_v,intercept_i, slope_i])
          
      except OSError as e:
         
          pass
      except ValueError as e:
          
          pass
      except ZeroDivisionError as e:
          pass
          
    ED = datetime.datetime.now()

    time_series = ED-ST
    Tlog = "Time for executing vehavg_instrecover_Ref.py　=> " + str(time_series)+"\n"
    wf = open("Timer/timer.txt" , mode='a')    
    wf.write(Tlog)
    wf.close()