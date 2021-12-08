#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Fri Mar 15 13:09:10 2019
output file.p,inthere have subdictionary to save every modules data in file.p

This function still use old version on Gomofs. Using zhao lei's multipy_modules_old,for getting temperature and depth together.

20 Feb 2020,Mingchao
    Modified the style of realpath and climpath for geting clim's data
    If the models'data aren't enough,you can use Amending_temp&depth_of_models.py to fix the data

Mar 4,2020 Mingchao
    Change the model of Gomofs to Jim's new model,only get temperatue
APr 27,2020 Mingchao
    Match emolt.dat and dictionary,get the emolt data doesn't exist in dictionary.
Apr 30,2020 Mingchao
    Combine emolt.dat with emolt_no_telemetry,you must run check_csv and process.py first before you run this one.
    Because emolt_no_telemetry got from check_csv.py and process.py
May 15,2020 Mingchao
     save dictionary.json to 'E:\Mingchao\result\mingchao_weekly' , then upload to student_drifter
@author: leizhao
"""
import pandas as pd
from datetime import datetime,timedelta
import time
#import multipy_modules_new as mm
import multiple_models as mm
import numpy as np
import json
import sys
import os
import ftplib

################################# Hardcodes ################################
end_time=datetime.utcnow()#-timedelta(days=2)#UTC time
start_time=end_time-timedelta(weeks=1) #get the time of start time
start_time_button = 'on'#if you used 'off',you will use 'end-time' of dictionary.json as start_time 
Host = '66.114.154.52'
UserName = 'huanxin'
Pswd = '123321'
remot_dir = '/mingchao_weekly'
local_folder = 'C:\\Weekly_Project\\Weekly_Project\\Mingchao\\result\\mingchao_weekly\\'   
#realpath=os.path.dirname(os.path.abspath(__file__)) # get the path of this code file
realpath=os.path.abspath('C:\\Weekly_Project\\Weekly_Project\\programe\\aqmain\\py')
parameterpath=realpath[::-1].replace('py'[::-1],'parameter'[::-1],1)[::-1]# get the path of parameter
telemetry_status='http://www.emolt.org/emoltdata/telemetry_status.csv'   #get the filepath and file name of telemetry status
#telemetry_status='E:/programe/aqmain/parameter/telemetry_status.csv'
    # download from web:'https://docs.google.com/spreadsheets/d/1uLhG_q09136lfbFZppU2DU9lzfYh0fJYsxDHUgMB1FM/edit?ts=5ba8fe2b#gid=0' 
#climpath=os.path.join(realpath,'clim')
climpath='/var/www/vhosts/emolt.org/huanxin_ftp/weekly_project/clim/'
#resultpath=realpath[::-1].replace('py'[::-1],'dictionary'[::-1],1)[::-1]  #get the path of result 
dictionarypath='/var/www/vhosts/emolt.org/httpdocs/emoltdata/dictionary.json' #filepath and filename of old dictionary 
#emolt_no_telemetry_path='E:\\Mingchao\\result\\mingchao_weekly\\emolt_QCed_no_telemetry.csv'
emolt_no_telemetry_path='/var/www/vhosts/emolt.org/huanxin_ftp/weekly_project/result/emolt_QCed_telemetry_and_wified.csv'
# emolt_QCed_path = 'https://www.nefsc.noaa.gov/drifter/emolt_QCed.csv'
emolt_QCed_df_save = '/var/www/vhosts/emolt.org/huanxin_ftp/weekly_project/result/dictionary.json'
###################################################################################

    
def read_telemetrystatus(path_name):
    """read the telementry_status, then return the useful data"""
    data=pd.read_csv(path_name)
    #find the data lines number in the file('telemetry_status.csv')
    for i in range(len(data['vessel (use underscores)'])):
        if data['vessel (use underscores)'].isnull()[i]:
            data_line_number=i
            break
    #read the data about "telemetry_status.csv"
    #telemetrystatus_df=pd.read_csv(path_name,nrows=data_line_number)
    telemetrystatus_df=pd.read_csv(path_name)
    as_list=telemetrystatus_df.columns.tolist()
    idex=as_list.index('vessel (use underscores)')
    as_list[idex]='Boat'
    telemetrystatus_df.columns=as_list
    for i in range(len(telemetrystatus_df)):
        telemetrystatus_df['Boat'][i]=telemetrystatus_df['Boat'][i].replace("'","")
        if not telemetrystatus_df['Lowell-SN'].isnull()[i]:
            telemetrystatus_df['Lowell-SN'][i]=telemetrystatus_df['Lowell-SN'][i].replace('，',',')
        if not telemetrystatus_df['logger_change'].isnull()[i]:
            telemetrystatus_df['logger_change'][i]=telemetrystatus_df['logger_change'][i].replace('，',',')
    return telemetrystatus_df

#def read_emolt_all(path='https://www.nefsc.noaa.gov/drifter/emolt.dat',endtime=datetime.now()):
def read_emolt_all(path='http://emolt.org/emoltdata/emolt.dat',endtime=datetime.utcnow()):
#def read_emolt_all(path='/home/jmanning/Mingchao/result/emolt_dat_all.csv',endtime=datetime.now()):
    """read the emolt data and fix a standard format, the return the standard data"""
    while True:
        emolt_df=pd.read_csv(path,sep='\s+',names=['vessel_n','esn','month','day','Hours','minutes','fracyrday',\
                                          'lon','lat','dum1','dum2','depth','rangedepth','timerange','temp','stdtemp','year'])
        if int(emolt_df['year'][len(emolt_df)-2])==endtime.year:
            break
        else:
            print('check the web:http://emolt.org/emoltdata/emolt.dat')
            time.sleep(600)
    return emolt_df

# def read_emolt(start,end,path='https://www.nefsc.noaa.gov/drifter/emolt.dat'):
def read_emolt(start,end,path='http://emolt.org/emoltdata/emolt.dat'):
#def read_emolt(start,end,path='/home/jmanning/Mingchao/result/emolt_dat_all.csv'):
    '''the start and end is represent the sart time and end time, the format is datetime.datetime
    function: return the emolt data, the time during start time and end time.
    '''
    emolt_df=read_emolt_all(path)   #emolt_df means emolt data, this data from website 'https://www.nefsc.noaa.gov/drifter/emolt.dat',we should avoid the update time when we use this function
    #screen out the data of telemetry in interval
    valuable_emolt_df=pd.DataFrame(data=None,columns=['vessel_n','esn','time','lon','lat','depth','temp'])#use to save the data from start time to end time
    for i in range(len(emolt_df)):
        emolt_time_str=str(emolt_df['year'].iloc[i])+'-'+str(emolt_df['month'].iloc[i])+'-'+str(emolt_df['day'].iloc[i])+' '+\
                                         str(emolt_df['Hours'].iloc[i])+':'+str(emolt_df['minutes'].iloc[i])+':'+'00'# the string of observation time
        emolt_time_str=str(emolt_df['year'].iloc[i])+'-'+str(emolt_df['month'].iloc[i])+'-'+str(emolt_df['day'].iloc[i])+' '+str(emolt_df['Hours'].iloc[i])+':'+str(emolt_df['minutes'].iloc[i])+':'+'00'# the string of observation time
        emolt_time=datetime.strptime(emolt_time_str,'%Y-%m-%d %H:%M:%S') #chang the observation time format as datetime.datetime. it is convenient to compare with start time and end time.
        if start<emolt_time<=end:# grab the data that time between start time and end time
                valuable_emolt_df=valuable_emolt_df.append(pd.DataFrame(data=[[emolt_df['vessel_n'][i],emolt_df['esn'][i],emolt_time,emolt_df['lon'][i],\
                #valuable_emolt_df=valuable_emolt_df.append(pd.DataFrame(data=[[emolt_df['vessel_n'][i],emolt_df['esn'][i],datetime.strptime(emolt_time_str,'%Y-%m-%d %H:%M:%S'),emolt_df['lon'][i],\
                                   emolt_df['lat'][i],emolt_df['depth'][i],emolt_df['temp'][i]]],\
                                   columns=['vessel_n','esn','time','lon','lat','depth','temp']))
    
    return valuable_emolt_df

def create_storedictionary(dictionary):
    '''function: give a empty dictionary, use to create the subdictionary'''
    dictionary['lat']={}
    dictionary['lon']={}
    dictionary['observation_T']={}
    dictionary['observation_H']={}
    dictionary['Doppio_T']={}
    dictionary['Doppio_H']={}
    dictionary['GoMOLFs_T']={}
    dictionary['GoMOLFs_H']={}
    dictionary['FVCOM_T']={}
    dictionary['FVCOM_H']={}
    dictionary['Clim_T']={}
    dictionary['NGDC_H']={}
    return dictionary

#def classify_by_boat(telemetry_status,start_time,end_time,dictionary,climpath):
def classify_by_boat(start_time_button,telemetry_status,start_time,end_time,dictionary,climpath,emolt_no_telemetry_path):
    """function: get the Doppio, GoMOLFs, FVCOM, Climate values
    
    input:
    telemetry_status: the file path and file name
    start_time:  start time, the format is datetime.datetime
    end _time: end time, the format is datetime.datetime
    dictionary:a dictionary that stores data for each models or an empty dictionary"""
    if start_time_button == 'off': # this is the case of using the endtime of previous dictionary 
        start_time_str=dictionary['end_time']  # if dict['end_time'] is wrong, please comment this code
        start_time=datetime.strptime(start_time_str,'%Y-%m-%d %H:%M:%S')
    else:
        start_time=start_time
    telemetrystatus_df=read_telemetrystatus(telemetry_status)# read the telemetry status data
    emolt_df = pd.read_csv(emolt_no_telemetry_path, index_col=0)
    emolt_df = emolt_df.drop_duplicates(['vessel','datet'])
    emolt_df = emolt_df.rename(columns={'vessel':'vessel_n','datet':'time','mean_temp':'temp'})
    emolt_df['time'] = pd.to_datetime(emolt_df['time'])
    emolt_df.index = range(len(emolt_df))
    #for i in range(len(emolt_df)):
    for i in emolt_df.index:
        if not start_time<emolt_df['time'][i]<=end_time:
            emolt_df = emolt_df.drop(i)
    emolt_df = emolt_df[emolt_df['flag']==0]
    
    #clean the index of valuable telementry data
    if len(emolt_df)>0:
        emolt_df.index=range(len(emolt_df)) 
        dictionary['end_time']=str(emolt_df['time'][len(emolt_df)-1])
    for j in range(len(telemetrystatus_df)):# loop boat name, If the name is new, then you need to create a new dataframe for the new name.
        vessel_name=telemetrystatus_df['Boat'][j]
        print(vessel_name)
        if vessel_name not in dictionary.keys():
            dictionary[vessel_name]={}#create a new dictionary under dictionary
            dictionary[vessel_name]=create_storedictionary(dictionary[vessel_name])# create mutiple subdictionary under dicitonary.
        
        for i in emolt_df.index:  #valuable_tele_df is the valuable telemetry data during start time and end time 
            if int(emolt_df['vessel_n'][i].split('_')[1])==telemetrystatus_df['Vessel#'][j]:
                ptime=emolt_df['time'][i] # the observation time
                print(ptime)
                latpt=float(emolt_df['lat'][i]) # the lat of observation
                lonpt=float(emolt_df['lon'][i]) #the lon of observation
                depthpt=float(emolt_df['depth'][i]) #the depth of observation
                temppt=float(emolt_df['temp'][i])
                try:     #try to get doppio data in the same location
                    DOPPIO = mm.get_doppio_fitting(latp=latpt,lonp=lonpt,depth='bottom',dtime=ptime,fortype='tempdepth')
                    if str(DOPPIO) == 'nan' or str(DOPPIO[0]) == 'nan':
                        dpo_temp,dpo_depth = mm.get_doppio_no_fitting(lat=latpt,lon=lonpt,depth=99999,time=ptime)
                        #print('DOPPIO_no_fitting:')
                    else:                        
                        dpo_temp = DOPPIO[0]
                        dpo_depth = DOPPIO[1]
                        #print('DOPPIO_fitting')
                except KeyboardInterrupt:
                    sys.exit()
                except:
                    dpo_temp,dpo_depth = np.nan,np.nan
                    #print('DOPPIO')
                try:    #try to get the gomofs data in the same location
                    #use Jim's method,added on 7/6/2020
                    GOMOFS = mm.get_gomofs_zl(dtime=ptime,latp=latpt,lonp=lonpt,depth='bottom',fortype='tempdepth')
                    if str(GOMOFS) == 'nan' or str(GOMOFS[0]) == 'nan':
                        gmf_temp,gmf_depth = mm.get_gomofs(date_time=ptime,lat=latpt,lon=lonpt,depth='bottom',mindistance=20)
                        #print('GOMOFS_no_fitting::')                    
                    else:
                        gmf_temp = GOMOFS[0] 
                        gmf_depth = GOMOFS[1]
                        #print('GOMOFS_zl_fitting:')   
                    #print ('gomfs finished')
                except KeyboardInterrupt:
                    sys.exit()
                except:
                    gmf_temp,gmf_depth = np.nan,np.nan
                    #print ('gomfs is nan')
                    #print('GOMOFS')
                try:
                    #FV_temp,FV_depth=mm.get_FVCOM_temp(latp=latpt,lonp=lonpt,dtime=ptime,depth=depthpt,fortype='tempdepth')
                    FVCOM = mm.get_FVCOM_fitting(latp=latpt,lonp=lonpt,dtime=ptime,depth='bottom',mindistance=2,fortype='tempdepth')
                    if str(FVCOM) == 'nan' or str(FVCOM[0]) == 'nan':
                        urlfvcom = mm.get_FVCOM_url(ptime)
                        FV_temp = mm.get_FVCOM_no_fitting(urlfvcom=urlfvcom,lati=latpt,loni=lonpt,dtime=ptime,depth=99999)
                        #FV_depth = np.nan
                        FV_depth = depthpt#using observation's depth
                        #print('FVCOM_no_fitting')
                    else:
                        FV_temp = FVCOM[0] 
                        FV_depth = FVCOM[1]
                        #print('FVCOM_fitting')
                except KeyboardInterrupt:
                    sys.exit()
                except:
                    FV_temp,FV_depth=np.nan,np.nan
                    #print('FVCOM')
                try:
                    ngdc_depth=mm.get_depth_bathy(loni=lonpt,lati=latpt)
                    #print('CLIMDEPTH:')
                except KeyboardInterrupt:
                    sys.exit()
                except:
                    ngdc_depth=np.nan
                    #print('CLIM DEPTH')
                try:
                    #climtemp=mm.getclim(lat1=latpt,lon1=lonpt,path=climpath,dtime=ptime)#store the data of climate history and ngdc
                    climtemp=mm.getclim(lat1=latpt,lon1=lonpt,path=climpath,dtime=ptime,var='Bottom_Temperature/BT_')
                    #print('CLIMTEMP:  666')
                    #print('one loop')
                except KeyboardInterrupt:
                    sys.exit()
                except:
                    climtemp=np.nan
                    #print('CLIM TEMP')
                data_list=[latpt,lonpt,float(temppt),float(depthpt),float(dpo_temp),float(dpo_depth),float(gmf_temp),float(gmf_depth),float(FV_temp),float(FV_depth),float(climtemp),float(ngdc_depth)]
                dictionary[vessel_name]=store_data(key=str(ptime),data_list=data_list,dictionary=dictionary[vessel_name])
                emolt_df=emolt_df.drop(i)  #if this line has been classify, delete this line
    return dictionary

def store_data(key,data_list,dictionary):
    '''give a list and key, store the value in the ditionary'''
    dictionary['lat'][key]=data_list[0]
    dictionary['lon'][key]=data_list[1]
    dictionary['observation_T'][key]=data_list[2]
    dictionary['observation_H'][key]=data_list[3]
    dictionary['Doppio_T'][key]=data_list[4]
    dictionary['Doppio_H'][key]=data_list[5]
    dictionary['GoMOLFs_T'][key]=data_list[6]
    dictionary['GoMOLFs_H'][key]=data_list[7]
    dictionary['FVCOM_T'][key]=data_list[8]
    dictionary['FVCOM_H'][key]=data_list[9]
    dictionary['Clim_T'][key]=data_list[10]
    dictionary['NGDC_H'][key]=data_list[11]
    return dictionary

#def update_dictionary(telemetry_status,start_time,end_time,dictionarypath,climpath):
def update_dictionary(start_time_button,telemetry_status,start_time,end_time,dictionarypath,climpath,emolt_no_telemetry_path,emolt_QCed_df_save):
    '''use to update the dictonary that use to store the model estimates at the observation points
    
    input:
        telemetry_status: the file path and file name
        start_time:  start time, the format is datetime.datetime
        end _time: end time, the format is datetime.datetime
        dictionarypath: the dictionary file path and file name 
        '''
    try: #read dictionary
        with open(dictionarypath,'r') as fp:
            dictionary = json.load(fp)
    except KeyboardInterrupt:
        sys.exit()
    except: 
        dictionary={}  
    #update dictionary 
    #obsdpogmf=classify_by_boat(telemetry_status,start_time,end_time,dictionary,climpath)  #running function to store new data from modules
    obsdpogmf=classify_by_boat(start_time_button,telemetry_status,start_time,end_time,dictionary,climpath,emolt_no_telemetry_path)
    #save updated dictionary
    with open(dictionarypath, 'w') as fp:
        json.dump(obsdpogmf, fp)
    with open(emolt_QCed_df_save, 'w') as fp:
        json.dump(obsdpogmf, fp)

def upload_weekly(Host, UserName, Pswd,remot_dir, local_folder):
    '''upload weekly result to student drifter'''
    ftp = ftplib.FTP(Host)
    ftp.login(UserName, Pswd)
    ftp.cwd(remot_dir)
    local_list = os.listdir(local_folder)
    for i in range(len(local_list)):
        command = 'STOR '+local_list[i]
        sendFILEName = local_folder+local_list[i]
        ftp.storbinary(command, open(sendFILEName,'rb'))
        print('upload '+local_list[i])
    ftp.quit()

###############################  MAIN  #########################################
#update_dictionary(telemetry_status,start_time,end_time,dictionarypath,climpath)   #that is a function use to update the dictionary
update_dictionary(start_time_button,telemetry_status,start_time,end_time,dictionarypath,climpath,emolt_no_telemetry_path,emolt_QCed_df_save)
#upload_weekly(Host, UserName, Pswd,remot_dir, local_folder)#upload to student drifter.If you don;t need,close this one