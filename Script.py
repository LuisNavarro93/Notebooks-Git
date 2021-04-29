# -*- coding: utf-8 -*-
"""

@author: Luis Navarro
"""
# Script
# =============================================================================
# Libraries 
import pandas as pd 
import numpy as np 
import matplotlib.pyplot as plt
plt.style.use("seaborn")
import seaborn as sns
from bs4 import BeautifulSoup
from mpl_toolkits import mplot3d
import math
# =============================================================================
# Functions
# Read XML files
def read_xml(file):
    print("File : ",file)
    with open(file) as f:
        data = f.read()   
    data_xml = BeautifulSoup(data, 'xml')
    print("\nWellbore name:",data_xml.find_all("nameWell")[0].text)
    print("Wellbore section:",data_xml.find_all("name")[0].text)
    print("Start date:",data_xml.find_all('dTimTrajEnd')[0].text)
    len_ = len(data_xml.find_all('statusTrajStation'))
    print("Final md :",data_xml.find_all('md')[len_-1].text,"[m]")
    print("Surveys:",len_,"\n\n")
    tvd = data_xml.find_all('incl')
    cols =['md','tvd','dispNs','dispEw','incl','azi','dls']
    well = pd.DataFrame()
    for col in cols:
        well[col] = [float(x.text) for x in data_xml.find_all(col)]
    well["neg_tvd"] = well["tvd"]*-1
    return(well)

# Plot axis and inverted
def plts_traj(data,xaxis,yaxis,titl,invert=""):
    plt.figure(figsize=(16,10))
    if invert == "invert":
        plt.plot(data[xaxis],data[yaxis])
        plt.xlabel(str(xaxis)) ; plt.ylabel(str(yaxis))
        plt.gca().invert_yaxis()
        plt.title(titl)
    else:
        plt.plot(data[xaxis],data[yaxis])
        plt.xlabel(str(xaxis)) ; plt.ylabel(str(yaxis))
        plt.title(titl)
    plt.show()
    
#plot actual vs planned trajectories profiles
def planact_traj(plan,act):
    fig=plt.figure(figsize=(10,7),dpi=100)
    fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(10,7))
    axes[0].plot(act["dispEw"],act["tvd"],label="Actual")
    axes[0].plot(plan["dispEw"],plan["tvd"],label="Plan")
    axes[0].set_xlabel("dispNs") ; axes[0].set_ylabel("TVD")  ; axes[0].legend() ;axes[0].invert_yaxis()
    axes[1].plot(act["dispEw"],act["dispNs"],label="Actual")
    axes[1].plot(plan["dispEw"],plan["dispNs"],label="Plan")
    axes[1].set_xlabel("dispEw") ; axes[1].set_ylabel("dispNs") ; axes[1].legend()
    plt.tight_layout()
    plt.show()   
    
#Dataframe creating having time indexed LAS files
def time_indexed_LAS(file):
    print("File:",file,"\n")
    with open(file, 'r') as f:
        text_ = f.readlines()[0:100]
    
    i = 0;
    for line in text_:
        #print("Line {}: {}".format(i,line.strip()))
        if "~A" in line.strip():
            start_line = i
            #print(line.strip())
            break
        #else: 
            #print(line.strip())
        i+=1
    
    #print("Start_Line:",start_line)
    def time_builder(file,row):
        with open(file, 'r') as f:
            lines_full  = f.readlines()[row:]
        print("total rows : ",len(lines_full))
        cols = str(lines_full[0])
        cols = cols.split()
        del cols[0]
        data = (lines_full[1:])
        data_list = []
        for i in range(len(data)):
            act = data[i].split()
            data_list.append(act)
            i+=1

        df = pd.DataFrame(data_list,columns = cols)
        datums = df.columns.difference(['TIME','DATE'])
        df[datums] = df[datums].astype(float)
        df["DATE"] = pd.to_datetime(df["DATE"])
        df["TIME"] = pd.to_timedelta(df["TIME"])
        df["DateTime"] = df["DATE"] + df["TIME"]
        df = df.drop(['TIME','DATE'],axis=1)
        df = df.replace(-999.250000, np.nan)
        print("Columns:\n",df.columns.values)
        print("Initial depth:",df["DEPT"][0])
        print("DeltaTime:",df["DateTime"][1]-df["DateTime"][0],"\n\n")
        return(df)
    
    
    df = time_builder(file,start_line)
    return(df)
#plotting well data
def well_plt(data,run):
    print(run)
    plots = list(data.columns.difference(['DateTime'])) 
    fig,axes = plt.subplots(1,len(plots), figsize=(20,20))
    for i,log in enumerate(plots):
        axes[i].plot(data[log],data['DateTime'],linewidth = 0.5)
        axes[i].set_ylim(data['DateTime'].min(),data['DateTime'].max())
        axes[i].invert_yaxis()
        axes[i].set_title(log,fontsize=8.5)
        axes[i].grid(color="black",linestyle = '--', linewidth = 0.5,axis="x")
    plt.show()
    print("\n\n")
    