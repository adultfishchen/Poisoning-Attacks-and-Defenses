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
import datetime
import math
import fnmatch
import warnings
import statistics as st
from sklearn import svm
from sklearn.svm import SVC
from sklearn.model_selection import GridSearchCV
from glob import glob

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
    #'''
    for edge in edges:
        lanes = edge.getLanes()
        for lane in lanes:
            Lane_dict[lane.getID()] = lane.getLength()
    #'''
    #Lane_dict["-111343195#2_0"] = 5
    
    if not os.path.exists('ins_veavg_SVM_A'):
      os.makedirs('ins_veavg_SVM_A')
    
    if not os.path.exists('Reference/'):
      os.makedirs('Reference/')
    
    with open("Reference/relationships_defense.csv", "w", newline='') as fp:    
      d = csv.writer(fp)
      d.writerow(["Lane","coefficient_1","coefficient_2","intercept"])
      
    #lane_list = ["-496253687#1_0","250710099#0_0","-24452786#6_0","-160253722#7_0","-24452786#2_0","71285598#5_0","108037210#0_0","-496332201#4_0","-286094870#6_0","-227913938#10_0","307096544#4_0"]
    warnings.filterwarnings("ignore")
    print("Starting SVM ...")
    for lane in Lane_dict.keys():
    
      
    #for lane in lane_list:  
          
      try:
            # Load Dataset
            data = pd.read_csv("SVM_ref/"+lane+".csv")
            #if len(data) > 11000:
            #  print("Too Large")
            #  pass
            #else:
            # target parameters            
            tamper = data[data['target'] == 0]
            untamper = data[data['target'] == 1]
            # Features            
            X = data[['instspeed', 'tamper_vehavg']]
            y = data['target']
    
            # Define SVM parameters
            parameters = {'kernel': ('linear', 'rbf'), 'C': [0.1,1, 10,100], 'gamma': [0.1, 1,10,100]}
            parameters = {'C': [0.1,1, 10,100], 'gamma': [0.1, 1,10,100]}
    
            # Build SVM            
            svc = SVC(kernel='linear')
    
            # GridSearch
            clf = GridSearchCV(svc, parameters, cv=5)
            clf.fit(X, y)
    
            # Apply best paramteres and train
            svm = SVC(kernel='linear', C=clf.best_params_['C'], gamma=clf.best_params_['gamma'])
            svm.fit(X,y)
    
                
            # get decision parameters
            w = svm.coef_[0]            
            a = -w[0] / w[1]
            xx = np.linspace(0, 120)
            yy = a * xx - (svm.intercept_[0]) / w[1]
            b = svm.intercept_[0]
                
               
            # plot             
            plt.scatter(tamper["instspeed"], tamper["tamper_vehavg"], color="red", label="tamper")
                
            plt.scatter(untamper["instspeed"], untamper["tamper_vehavg"], color="green", label="untamper")
            
                        
            plt.plot(xx, yy, 'k-', label='SVM Decision Boundary')
            # Equation
            equation = f"{w[0]:.2f} * instspeed + {w[1]:.2f} * veh_avg + {b:.2f} = 0"
            plt.annotate(equation, xy=(0.05, 0.05), xycoords='axes fraction', fontsize=8)
    
    
            # Legend
            plt.legend(loc='upper left')
           
            plt.title(str(lane)+"_ins_vehavg_SVM Classification")
            plt.xlabel("Instspeed$_p$")
            plt.ylabel("vehavg$_p$")
            plt.xlim([-10, 30])             
            plt.ylim([-10, 30])     
            plt.xticks(range(-10, 31, 2))           
            plt.yticks(range(-10, 31, 2))
            
            # Save pic 
            plt.savefig("ins_veavg_SVM_A/"+lane+".png")
            # clear
            plt.clf()
            
            with open("Reference/relationships_defense.csv", "a", newline='') as fp:    
              d = csv.writer(fp)
              d.writerow([lane,w[0], w[1],b])
            
      except OSError as e:
          #print(e)
          pass
      except ValueError as e:
          #print(e)
          pass
      except Exception as e:
          #print(e)
          pass
          
    ED = datetime.datetime.now()

    time_series = ED-ST
    Tlog = "Time for executing SVM.py?�?> " + str(time_series)+"\n"
    wf = open("Timer/timer.txt" , mode='a')    
    wf.write(Tlog)
    wf.close()      
