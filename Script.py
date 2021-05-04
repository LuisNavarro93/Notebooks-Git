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
import matplotlib.dates as mdates
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
        print("Total rows : ",len(lines_full))
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
        df
        df = df.replace(-999.250000, np.nan)
        print("Columns:\n",df.columns.values)
        print("Initial depth:",df["DEPT"][0])
        print("Initial date:", df["DateTime"][0].strftime('%d-%B-%Y'))
        print("DeltaTime:",df["DateTime"][1]-df["DateTime"][0],"\n\n")
        return(df)
    
    df = time_builder(file,start_line)
    return(df)
#plotting well data
def well_plt(data,info):
    plt.style.use("seaborn")
    date_format = mdates.DateFormatter("%d-%B %H:%M")
    print("Plot:",info[0],"\tSection:",info[1])
    plots = list(data.columns.difference(['DateTime'])) 
    fig,axes = plt.subplots(1,len(plots), figsize=(20,20),sharey=True)
    for i,log in enumerate(plots):
        axes[i].plot(data[log],data['DateTime'],linewidth = .8)
        axes[i].set_ylim(data['DateTime'].min(),data['DateTime'].max())
        axes[i].invert_yaxis()
        axes[i].set_title(log,fontsize=8)
        axes[i].yaxis.set_major_formatter(date_format)
    plt.show()
    print("\n\n")
#plotting logs vs time    
def time_plts(list_,data,info):
    print("Plot:",info[0],"\tSection:",info[1])
    plt.style.use("bmh")
    date_format = mdates.DateFormatter("%d-%B %H:%M")
    fig,axes = plt.subplots(len(list_),1,figsize=(15,8),sharex=True)
    for i,log in enumerate(list_):
        axes[i].plot(data["DateTime"],data[list_[i]],linewidth = 0.5,color="steelblue")
        axes[i].set_ylabel(log,fontsize=15)
        axes[i].xaxis.set_major_formatter(date_format)
    axes[i].set_xlabel("DateTime",fontsize=15)
    plt.tight_layout()
#Plotting line with date slider
def date_plts(list_,data,info,inf,sup):
    print("Plot:",info[0],"\tSection:",info[1])
    plt.style.use("bmh")
    date_format = mdates.DateFormatter("%d-%B %H:%M")
    fig,axes = plt.subplots(len(list_),1,figsize=(15,8),sharex=True)
    for i,log in enumerate(list_):
        axes[i].plot(data["DateTime"],data[list_[i]],linewidth = 0.5,color="steelblue")
        axes[i].set_ylabel(log,fontsize=15)
        axes[i].xaxis.set_major_formatter(date_format)
    axes[i].set_xlabel("DateTime",fontsize=15)
    axes[i].set_xlim(inf,sup)
    plt.tight_layout()   
#Drilling process selector
def drilling_process_fell(data,start_depth):
    """by Stephen Fell
    HDTV : Hole Depth
    BONB : Bit on Bottom
    """
    data["DateTime"] = pd.to_datetime(data["DateTime"])
    data['HDTH'] = data["DEPT"].cummax().apply(lambda x: x if (x > start_depth) else np.nan)
    data['BONB'] = data['HDTH'] - data['DEPT']
    data['BONB'] = data['BONB'].apply(lambda x: 0 if (x < 0.5) else 1)
    tflo = data["TFLO"].to_list()
    rpm = data["RPM"].to_list()
    bonb = data["BONB"].to_list()
    flg = []
    for i in range(len(data)):
        if (bonb[i] == 0) and (tflo[i] > 20) and (rpm[i] > 20):
            flg.append(1)
        else :
            flg.append(0)
        i =+ 1
    
    data["Flag"] = flg
    return(data)
#Plotting depth and flags
def drill_flag(data,info):
    print("\nPlot:",info[0],"\tSection:",info[1])
    date_format = mdates.DateFormatter("%d-%B %H:%M")
    fig, ax = plt.subplots(figsize = (15,8))
    ax.plot(data['DateTime'], data['DEPT'], label='Bit Depth (DEPT)')
    ax.plot(data['DateTime'], data['HDTH'], label='Hole Depth (HDTH)',alpha=.7)
    ax.invert_yaxis()
    ax.set_ylabel("Depth",fontsize=15)
    fig.legend()
    ax1 = ax.twinx()
    ax1.scatter(data['DateTime'], data['Flag'], marker='|', color='green', label='Drilling Flag')
    ax1.set_ylim(0.5,20)
    ax1.set_yticklabels([])
    ax.set_xlabel("DateTime",fontsize=15)
    ax1.xaxis.set_major_formatter(date_format)
    fig.legend()
    plt.show()

def date_scatter_plts(list_,data,info,inf,sup):
    print("Plot:",info[0],"\tSection:",info[1])
    plt.style.use("bmh")
    date_format = mdates.DateFormatter("%d-%B %H:%M")
    fig,axes = plt.subplots(len(list_),1,figsize=(15,8),sharex=True)
    for i,log in enumerate(list_):
        axes[i].scatter(data["DateTime"],data[list_[i]],color="steelblue",marker="*",s=2)
        axes[i].set_ylabel(log,fontsize=15)
        axes[i].xaxis.set_major_formatter(date_format)
    axes[i].set_xlabel("DateTime",fontsize=15)
    axes[i].set_xlim(inf,sup)
    plt.tight_layout()
#Line reader for logs
def logs_LAS(file):
    print("File:",file)
    with open(file, 'r') as f:
        text_ = f.readlines()[27:100]

    for line in text_:
        print(line.strip())
        if "#" in line.strip():
            break
#Bloxplot of log in runs
def boxplt_logs(files,log,label,info):
    print(label)
    f,axes = plt.subplots(1,len(files),figsize=(12,5),sharey=True)
    i = 0 
    for file in files:
        axes[i].boxplot(file[log].dropna(),notch=True,patch_artist=True)
        axes[i].set_title(info[i])
        axes[i].set_xticks([])
        i+=1           
    plt.tight_layout()
    plt.show()
#Depth plotting
def depth_plts(data,list_):
    plt.style.use("bmh")
    fig,axes = plt.subplots(1,len(list_),figsize=(10,12),sharey=True)
    for i,log in enumerate(list_):
        axes[i].scatter(data[list_[i]],data["DEPT"],marker = "*",s = 0.5,color="steelblue")
        axes[i].set_xlabel(log,fontsize=15)
        axes[i].invert_yaxis()
    axes[0].set_ylabel("Depth",fontsize=15)
    plt.tight_layout()
#Stick&Slip Severity 
def ss_severity(data):
    ss_list = data["Stick_RT"].to_list()
    rpm_list = data["RPM"].to_list()
    ss_severity = []
    ss_categorical = []
    ss_categorical_txt = []
    for i in range(len(data)):
        try:
            s_v = (ss_list[i]/(2*rpm_list[i]))*100
            
        except ZeroDivisionError:
            s_v = 0

        ss_severity.append(s_v)
        
        if (s_v < 40) or (math.isnan(s_v)):
            cat_v = 0 #none
            cat_t = "None or Low"

        elif ((s_v > 40) and (s_v < 80)):
            cat_v = 1   # Medium
            cat_t = "Medium"
            
        elif ((s_v > 80) and (s_v < 100)):
            cat_v = 2   # High
            cat_t = "High"

        elif (s_v > 100):
            cat_v = 3  #Severe
            cat_t = "Severe"
        
        ss_categorical.append(cat_v)
        ss_categorical_txt.append(cat_t)
    data["ss_severity"] = ss_severity
    data["ss_categorical"] = ss_categorical
    data["ss_categorical_txt"] = ss_categorical_txt
    
    return(data)

    
   


    
