# Routine to check Lowell Instrument data from AWS 
# This "_status" version just counts the number of hauls from each vessel
# This is a reduced version of the routine that plot actual hauls, see "read_s3_eMOLT.py" which is an addition to Carles's original code.
# Requires hardcode specification of mac addresses for each vessel (see section below).

import boto3
import os
import pandas as pd
import numpy as np
import io

## HARDCODES ###
correct_dep=10. # correction for atmos pressure
frac_dep=0.75#0.85 # fraction of the depth consider "bottom"
min_depth=15.0 # minimum depth (meters) acceptable for a cast
min_haul_time=5 # number of minutes considered for hauling on deck
 
vessel=['Beast_of_Burden','Kathyrn_Marie','Mary_Elizabeth','Miss_Emma','Princess_Scarlett']
mac=['00-1e-c0-6c-75-1d/','00-1e-c0-6c-76-10/','00-1e-c0-6c-74-f1/','00-1e-c0-4d-bf-c9/','00-1e-c0-6c-76-19/']
#vessel=['Beast_of_Burden']
#mac=['00-1e-c0-6c-75-1d/']

# eMOLT credentials (removed for github posting)
access_key = ''
access_pwd = ''
s3_bucket_name = ''  # bucket name
path = 'aws_files/'  # path to store the data

#Accessing the S3 buckets using boto3 client
s3_client = boto3.client('s3')
s3 = boto3.resource('s3',
                    aws_access_key_id=access_key,
                    aws_secret_access_key=access_pwd)

#Getting data files from the AWS S3 bucket as denoted above 
my_bucket = s3.Bucket(s3_bucket_name)
bucket_list = []
for k in range(len(vessel)):
    for file in my_bucket.objects.filter(Prefix=mac[k]):  # write the subdirectory name mac add
        file_name = file.key
        if (file_name.find(".csv") != -1) or (file_name.find(".gps") != -1): # JiM added gps
            bucket_list.append(file.key)
    length_bucket_list = (len(bucket_list))

#l_downloaded = os.listdir(path) 
#bucket_list = [e for e in bucket_list if e not in l_downloaded] # new files not yet downloaded


# Reading the individual files from the AWS S3 buckets and putting them in dataframes 
ldf_pressure = []  # Initializing empty list of dataframes
ldf_temperature = []
ldf_gps =[]
for file in bucket_list:
    obj = s3.Object(s3_bucket_name, file)
    data = obj.get()['Body'].read()
    try:
        if ('Temperature' in os.path.basename(file)) & (file[0:-16]+'.gps' in bucket_list):
            df = pd.read_csv(io.BytesIO(data), header=0, delimiter=",", low_memory=False)
            ldf_temperature.append(df)
        elif ('Pressure' in os.path.basename(file)) & (file[0:-13]+'.gps' in bucket_list):
            df = pd.read_csv(io.BytesIO(data), header=0, delimiter=",", low_memory=False)
            ldf_pressure.append(df)
        elif 'gps' in os.path.basename(file):
            df = pd.read_csv(io.BytesIO(data), header=0, delimiter=",", low_memory=False) # need to read this differently
            ldf_gps.append(df)
    except:
        print('Not working', file)

# Note: ldf_pressure, ldf_temperature,ldf_gps are lists of dataframes
# merging the dataframes
count=0
filenames = [i for i in bucket_list  if 'gps' in i] # where bucket_list is 3 times as many elements as filenames
for j in range(len(ldf_gps)): # only process those with a GPS
    if max(ldf_pressure[j]['Pressure (dbar)'])>min_depth: # only process those that were submergedmore than "min_depth" meters
        lat=ldf_gps[j].columns[0].split(' ')[1][1:]# picks up the "column name" of an empty dataframe read by read_csv
        lon=ldf_gps[j].columns[0].split(' ')[2]
        ldf_temperature[j]['ISO 8601 Time']=pd.to_datetime(ldf_temperature[j]['ISO 8601 Time'])
        dfall=ldf_temperature[j]
        dfall=dfall.set_index('ISO 8601 Time')
        dfall['depth (m)']=ldf_pressure[j]['Pressure (dbar)'].values-correct_dep
        dfall['lat']=lat[1:]# removes the "+"
        dfall['lon']=lon
        dfall=dfall[dfall['depth (m)']>frac_dep*np.max(dfall['depth (m)'])] # get bottom temps
        ids=list(np.where(np.diff(dfall.index)>np.timedelta64(min_haul_time,'m'))[0])# index of new hauls
        count=count+len(ids)
        v=vessel[np.where(np.array(mac) == filenames[j][:18])[0][0]]
        if lat[0:2].isdigit():
            print(v+' has '+str(len(ids)+1)+' hauls at '+str(lat)+'N, '+str(lon)+'W in '+filenames[j][18:-4])
        else:
            print(v+' has '+str(len(ids)+1)+' hauls with no GPS in '+filenames[j][18:-4])
            
print('\nTotal hauls ='+str(count))