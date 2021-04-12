#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 31 15:47:29 2020
Concatenated each vessel's raw data to one file named likes 'Virginia_Marise_hours.csv'.
Modified by Huanxin to emolt machine
Input:raw data from check_csv.py
Output:Vessel name+_hours.csv
@author: Jim&Mingchao
"""
import conversions as cv
import os
import pandas as pd
import zlconversions as zl
from datetime import datetime,timedelta
from pylab import mean, std

#Hardcodes
input_dir='/home/jmanning/leizhao/programe/raw_data_match/result/checked/'
input_dir='/var/www/vhosts/emolt.org/huanxin_ftp/weekly_project/classified/'
#end_time=datetime.now()
end_time=datetime.utcnow()
start_time=end_time-timedelta(days=170)
#start_time=end_time-timedelta(weeks=1)
Hours_save='/home/jmanning/Mingchao/result/Hours_data/'
Hours_save='/var/www/vhosts/emolt.org/huanxin_ftp/weekly_project/Hours_data/'
    
#main
allfile_lists=zl.list_all_files(input_dir)
file_lists=[]#store the path of every vessel's files
hoursfile_lists=zl.list_all_files(Hours_save)
#filter the raw files and store in file_lists
for file in allfile_lists:
   if file[len(file)-4:]=='.csv':
     file_lists.append(file)
#print (file_lists)
try:
    for file in file_lists: # loop raw files 
        print (file)        
        fpath,fname=os.path.split(file)  #get the file's path and name
        time_str=fname.split('.')[0].split('_')[2]+' '+fname.split('.')[0].split('_')[3]
        print(time_str)
        #GMT time to local time of file
        time_gmt=datetime.strptime(time_str,"%Y%m%d %H%M%S")
        if time_gmt<start_time or time_gmt>end_time:
            continue
        # now, read header and data of every file  
        
        header_df=zl.nrows_len_to(file,2,name=['key','value']) #only header 
        data_df=zl.skip_len_to(file,2) #only data
        #print (data_df)
        value_data_df=data_df.loc[(data_df['Depth (m)']>0.85*max(data_df['Depth (m)']))]  #filter the data
        
        value_data_df=value_data_df.iloc[7:]   #delay several minutes to let temperature sensor record the real bottom temp
       
        value_data_df=value_data_df.loc[(value_data_df['Temperature (C)']>mean(value_data_df['Temperature (C)'])-3*std(value_data_df['Temperature (C)'])) & \
                            (value_data_df['Temperature (C)']<mean(value_data_df['Temperature (C)'])+3*std(value_data_df['Temperature (C)']))]  #Excluding gross error
        
        value_data_df.index = range(len(value_data_df))  #reindex
        #print (range(len(value_data_df)))
        print (value_data_df)
        value_data_df['Datet(Y/m/d)']=1 #create a new column for saving another time style of '%Y-%m-%d'
        
        for i in range(len(value_data_df)):
            value_data_df['lat'][i],value_data_df['lon'][i]=cv.dm2dd(value_data_df['lat'][i],value_data_df['lon'][i])
            #value_data_df['Datet(Y/m/d)'][i]=datetime.strptime(value_data_df['Datet(GMT)'][i],'%Y-%m-%d %H:%M:%S')
        
        Hours_df=pd.DataFrame(data=None,columns=['time','lat','lon','depth','temp','new_time'])
        Hours_df['time']=value_data_df['datet(GMT)']
        Hours_df['lat']=value_data_df['lat']
        Hours_df['lon']=value_data_df['lon']
        Hours_df['depth']=value_data_df['Depth (m)']
        Hours_df['temp']=value_data_df['Temperature (C)']
        #value_data_df['Datet(Y/m/d)']=pd.to_datetime(value_data_df['Datet(Y/m/d)'])#change the time style to datetime
        Hours_df['new_time']=value_data_df['datet(GMT)']
        print ('111111111111111')
        if not os.path.exists(Hours_save+file.split('/')[8]):
            os.makedirs(Hours_save+file.split('/')[8])
        Hours_df.to_csv(os.path.join(Hours_save+file.split('/')[8]+'/',file.split('/')[8]+'#'+file.split('/')[10]),index=0)
        hoursfile_lists=zl.list_all_files(Hours_save+file.split('/')[8]+'/')
        dl=[]
        for k in range(len(hoursfile_lists)):
            dl.append(pd.read_csv(hoursfile_lists[k],index_col=None))#contact values belong to one vessel
        new_df=pd.concat(dl)
        new_df.drop_duplicates(subset=['time','depth'],inplace=True)
        new_df=new_df.sort_values(by='time',axis=0,ascending=True)#sorting by the column of time
        new_df.index=range(len(new_df))
        new_df.to_csv(os.path.join(Hours_save+file.split('/')[8]+'/',hoursfile_lists[k].split('#')[0].split('/')[6]+'_hours.csv'),index=0)
        
except:
    print('check if the files exists')
         
