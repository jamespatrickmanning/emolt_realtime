# -*- coding: utf-8 -*-
"""
Created on Thu Sep 30 01:19:40 2021

@author: xhx50
"""

# -*- coding: utf-8 -*-
"""
Created on Mon Mar 7 13:16:01 2016
@author: hxu
"""

# routine to process Aquatech 530TD data
# where it plots the record and generates output file


import matplotlib.pyplot as plt
import matplotlib.dates as dates
from pylab import *
from pandas import *
import os
import glob
import pandas as pd
#from datetime import datetime


##################################
####################################### please modify below
files=sorted(glob.glob('aq/*.csv'))
for fn in files:
    
    
    dfname=read_csv(fn,sep=',',skiprows=2,nrows=1)
    df_id_name=dfname.ix[0][1].split('_')
    #fn='Logger_sn_1724-44_data_20160125_073552.csv'
    #fn=event.src_path # where I have deleted the "units" row and fixed date to make it easier
    #print fn
    fnout=str(fn)[3:-4]
    ######################################
    '''
    Modify input file below only if you need 
    '''
    ####################################
    
    sn=fn.split('_')[2]
    tit=df_id_name[1]+df_id_name[0]
    #tit=fn.split('_')[2]+'_'+fn.split('_')[4]+fn.split('_')[5][:-4]
    path = '/home/hxu/github/ap2s/aq_pic/'   # where you want to save the output files
    ##################################
    ##################################
    fnoutdir=''
    
    def parse(datet):
        from datetime import datetime
        #dt=datetime.strptime(datet,'%m/%d/%Y %H:%M:%S PM')
        dt=datetime.strptime(datet,'%m/%d/%Y %I:%M:%S %p')
        #dt=datetime.strptime(datet,'%H:%M:%S %m/%d/%Y')
        return dt
    try:
        
        df=read_csv(fn,sep=',',skiprows=33,parse_dates={'datet':[1]},header=None,index_col='datet',date_parser=parse)#creat a new Datetimeindex
    except:
        #print 'no data in '+fn
        continue 
    
    
    #df.index=df.index+pd.tseries.timedeltas.to_timedelta(4, unit='h')  #, chage it to UTC time
    df['yd']=df.index.dayofyear+df.index.hour/24.+df.index.minute/60./24.+df.index.second/60/60./24.-1.0 #creates a yrday0 field
    #output_fmt=['yd','Unnamed: 4','Unnamed: 10']
    #dfp=df.reindex(columns=output_fmt)# found I needed to generate a new dataframe to print in this order
    #df.to_csv(fn+'.out',float_format='%10.2f',header=False)
    
    #
    df['depth']=(df[9]) #get depth
    df=df.ix[(df['depth']>0.90*mean(df['depth']))]  # get rid of shallow data
    #df=df.ix[(df['depth']>mean(df['depth'])-3*std(df['depth'])) & (df['depth']<mean(df['depth'])+3*std(df['depth']))] # reduces time series to deep obs
    #df['temp']=(df['Unnamed: 3'])#*1.8)+32.0
    df['temp']=(df[3])#*1.8)+32.0
    df=df.ix[(df['temp']>mean(df['temp'])-3*std(df['temp'])) & (df['temp']<mean(df['temp'])+3*std(df['temp']))] # reduces time series to deep obs
    #print len(df)
    
    for o in list(reversed(range(len(df)))):
        if (df.index[o]-df.index[o-1])>=Timedelta('0 days 00:30:00') or o==0: 
            df=df.ix[o:]
            break
            
    #df['']
    fig=plt.figure()
    ax1=fig.add_subplot(211)
    #df['temp'].plot()
    ax1.plot(df.index,df['temp'],'red')
    ax1.set_ylabel('Temperature (Celius)')
    
    try:    
        if max(df.index)-min(df.index)>Timedelta('0 days 04:00:00'):
            ax1.xaxis.set_major_locator(dates.HourLocator(interval=(max(df.index)-min(df.index)).seconds/3600/6))# for hourly plot
        else: 
            ax1.xaxis.set_major_locator(dates.MinuteLocator(interval=(max(df.index)-min(df.index)).seconds/60/6))# for minutely plot
    except:
        #print fn+'  data is too few'
        continue
    ax1.xaxis.set_major_formatter(dates.DateFormatter('%D %H:%M'))
    ax1.set_xlabel('')
    try:
        ax1.set_xticklabels([])
    except:
        #print fn+'  data is too few'
        continue
    ax1.grid()
    ax12=ax1.twinx()
    ax12.set_title(tit)
    ax12.set_ylabel('Fahrenheit')
    ax12.set_xlabel('')
    ax12.set_xticklabels([])
    ax12.set_ylim(np.nanmin(df['temp'].values)*1.8+32,np.nanmax(df['temp'].values)*1.8+32)
    
    
    maxtemp=str(int(round(max(df['temp'].values),2)*100))
    if len(maxtemp)<4:
        maxtemp='0'+maxtemp
    mintemp=str(int(round(min(df['temp'].values),2)*100))
    if len(mintemp)<4:
        mintemp='0'+mintemp
    meantemp=str(int(round(np.mean(df['temp'].values),2)*100))
    if len(meantemp)<4:
        meantemp='0'+meantemp
    sdeviatemp=str(int(round(np.std(df['temp'].values),2)*100))
    for k in range(4):
      if len(sdeviatemp)<4:
        sdeviatemp='0'+sdeviatemp
    
    time_len=str(int(round((df['yd'][-1]-df['yd'][0]),3)*1000))
    for k in range(3):
        if len(time_len)<3:
            time_len='0'+time_len
    #print time_len
    meandepth=str(abs(int(round(np.mean(df['depth'].values),0))))
    #print df['depth']
    rangedepth=str(abs(int(round(max(df['depth'].values-min(df['depth'].values)),0))))
    for k in range(3):
        if len(rangedepth)<3:
            rangedepth='0'+rangedepth
    #print 'rangedepth'+rangedepth
    
    for k in range(3):
        if len(meandepth)<3:
            meandepth='0'+meandepth
    #print meandepth        
    #print meantemp
    
    ax1.text(0.95, 0.9, 'mean temperature='+str(round(np.mean(df['temp'].values*1.8+32),1))+'F',
            verticalalignment='top', horizontalalignment='right',
            transform=ax1.transAxes,
            color='green', fontsize=15)
    ax2=fig.add_subplot(212)
    #df['depth'].plot()
    ax2.plot(df.index,df['depth'].values)
    ax2.invert_yaxis()
    ax2.set_ylabel('Depth (Meters)')
    #ax2.set_xlabel(df.index[0].year)
    ax2.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
    ax2.grid()
    ax2.set_ylim(max(df['depth'].values),min(df['depth'].values))
    ax2.text(0.95, 0.9, 'mean depth='+str(round(np.mean(df['depth'].values),0))+'m',
            verticalalignment='top', horizontalalignment='right',
            transform=ax2.transAxes,
            color='green', fontsize=15)
    
    ax22=ax2.twinx()
    ax22.set_ylabel('Fathoms')
    #ax22.set_ylim(np.nanmin(df['depth'].values)/1.8288,np.nanmax(df['depth'].values)/1.8288)
    ax22.set_ylim(min(df['depth'].values)/1.8288,max(df['depth'].values)/1.8288)
    ax22.invert_yaxis()
    '''
    if max(df.index)-min(df.index)>Timedelta('0 days 04:00:00'):
        ax1.xaxis.set_major_locator(dates.HourLocator(interval=(max(df.index)-min(df.index)).seconds/3600/6))# for hourly plot
    else: 
        ax1.xaxis.set_major_locator(dates.MinuteLocator(interval=(max(df.index)-min(df.index)).seconds/60/6))# for minutely plot
    '''
    ax2.xaxis.set_major_formatter(dates.DateFormatter('%D %H:%M'))
    plt.gcf().autofmt_xdate()    
    ax2.set_xlabel('UTC TIME')
    
    #ax2.xaxis.set_minor_locator(dates.HourLocator(interval=0)
    #ax2.xaxis.set_minor_formatter(dates.DateFormatter('%H'))
    #ax2.xaxis.set_major_locator(dates.DayLocator(interval=4))
    #ax2.xaxis.set_major_formatter(dates.DateFormatter('%b %d'))
    
    fnout=path+fnout[5:]
    #fnout = os.path.join(path, fnout[5:])
    #print fnout
    plt.savefig(fnout+'.png')
    plt.savefig(fnout+'.ps')
    
    # get file ready for ORACLE
    df['site']=fnout[1:3].upper()+fnout[3:5]
    df['salt']='99.999'
    df['sn']=sn[1:4]+sn[5] # needed to comply with ORACLE table constraints
    df['ps']=fnout[5:7]
    output_fmt=['site','sn','ps','yd','temp','salt','depth','depth']
    dfout=df.reindex(columns=output_fmt)
    dfout.to_csv(fnoutdir+fnout+'.dat',float_format='%10.4f',header=False)
