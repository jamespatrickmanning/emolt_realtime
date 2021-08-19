# -*- coding: utf-8 -*-
"""
Created on Wed Aug 18 20:01:57 2021

@author: xavier
"""

#@title gomofs (functions for extracting GOMOFS output) { form-width: "10%" }
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 25 15:37:42 2019
gets the output from Gulf of Maine Ocean Forecast System with function get_gomofs
@author: Lei Zhao with some help from Vitalli and JiM
Requires his "zlconversions" module 

Modification: March 15, 2019 - added a function(get_gomofs_url_forcast(date,forecastdate=1))
Modification: Feb 28, 2020 - made a much simpler function "get_gomofs" to get bottom temp and renamed Lei Zhao's as "get_gomofs_zl" 
Note: We might come back to Lei Zhao fancier way to fit the data but here we use the nearest node.
"""
#!pip install netCDF4 # this can be commented out after 1st run
import netCDF4
import datetime
import numpy as np
import math
import time
import zlconversions as zl 
def get_gomofs_url(date):
    """
    the format of date is a datetime such as datetime.datetime(2019, 2, 27, 11, 56, 51, 666857)
    returns the url of data
    
    JiM modified Jan 2021 to get old files from NCEI and recent from CO-OPS servers
    JiM modified Feb 2021 to get forecast files
    """
#    print('start calculate the url!') 
#    date=date+datetime.timedelta(hours=4.5)
    date_str=date.strftime('%Y%m%d%H%M%S')
    hours=int(date_str[8:10])+int(date_str[10:12])/60.+int(date_str[12:14])/3600.
    tn=int(math.floor((hours)/6.0)*6)  ## for example: t12z the number is 12
    tstr='t'+str(tn).zfill(2)+'z'
    if round((hours)/3.0-1.5,0)==tn/3:
        nstr='n006'       # nstr in url represent nowcast string: n003 or n006
    else:
        nstr='n003'
    # Jim changed 7/6/2020
    #print(date)
    #print(datetime.date.today())
    if date.date()<=datetime.datetime.now().date()-datetime.timedelta(days=7):
        #if date<=datetime.datetime(2020,12,1,0,0,0): #old gomofs files are on NCEI
        url='https://www.ncei.noaa.gov/thredds/dodsC/model-gomofs-files/'\
            +str(date.year)+'/'+str(date.month).zfill(2)+'/nos.gomofs.fields.'+nstr+'.'+date_str[:8]+'.'+tstr+'.nc'
    else: # recent files are stored on the co-ops server
        if date<datetime.datetime.now(): # get "nowcast"
            url='https://opendap.co-ops.nos.noaa.gov/thredds/dodsC/NOAA/GOMOFS/MODELS/'\
            +date_str[:4]+'/'+date_str[4:6]+'/'+date_str[6:8]+'/nos.gomofs.fields.'+nstr+'.'+date_str[:8]+'.'+tstr+'.nc'
        else: # JIM added the following "forecast" in Feb 2021
            #now=datetime.datetime.now()
            #midnight=datetime.datetime(now.year,now.month,now.day,0,0,0)
            #hours=int(round((now-midnight).total_seconds()/60/60))
            fn=int(math.floor((hours)/3.0)*3) 
            url='https://opendap.co-ops.nos.noaa.gov/thredds/dodsC/NOAA/GOMOFS/MODELS/'\
            +date_str[:4]+'/'+date_str[4:6]+'/'+date_str[6:8]+'/nos.gomofs.fields.f'+str(fn).zfill(3)+'.'+date_str[:8]+'.t00z.nc'
        
    return url


def get_gomofs_url_forecast(date,forecastdate=True):
    """
    same as get_gomofs_url but gets the forecast file instead of the nowcast
    where "date" is a datatime like datetime.datetime(2019, 2, 27, 11, 56, 51, 666857)
    forecastdate like date or True
    return the url of data
    """
    if forecastdate==True:  #if forcastdate is True: default the forcast date equal to the time of choose file.
        forecastdate=date
    date=date-datetime.timedelta(hours=1.5)  #the parameter of calculate txx(eg:t00,t06 and so on)
    tn=int(math.floor(date.hour/6.0)*6)  #the numer of hours in time index: eg: t12, the number is 12
    ymdh=date.strftime('%Y%m%d%H%M%S')[:10]  #for example:2019011112(YYYYmmddHH)
    tstr='t'+str(tn).zfill(2)+'z'  #tstr: for example: t12
    fstr='f'+str(3+3*math.floor((forecastdate-datetime.timedelta(hours=1.5+tn)-datetime.datetime.strptime(ymdh[:8],'%Y%m%d')).seconds/3600./3.)).zfill(3)#fnstr:the number in forcast index, for example f006 the number is 6
    url='http://opendap.co-ops.nos.noaa.gov/thredds/dodsC/NOAA/GOMOFS/MODELS/'\
    +ymdh[:6]+'/nos.gomofs.fields.'+fstr+'.'+ymdh[:8]+'.'+tstr+'.nc'
    return url

def get_gomofs(date_time,lat,lon,mindistance=20):# JiM's simple version for bottom temp
    """
    JiM's simplified version of Lei Zhao's function gets only bottom temp
    the format time(GMT) is: datetime.datetime(2019, 2, 27, 11, 56, 51, 666857)
    lat and lon use decimal degrees where lon is negative number
    returns the BOTTOM temperature (degC) of specify location
    HARDCODED TO RETURN BOTTOM TEMP
    """
    rho_index=0 # for bottom layer
    if not gomofs_coordinaterange(lat,lon):
        print('lat and lon out of range in gomofs')
        return np.nan
    if date_time<datetime.datetime.strptime('2018-07-01 00:00:00','%Y-%m-%d %H:%M:%S'):
        print('Time out of range, time start :2018-07-01 00:00:00z')
        return np.nan
    if date_time>datetime.datetime.utcnow()+datetime.timedelta(days=3): #forecast time under 3 days
        print('beyond the forecast time of 3 days')
        return np.nan
    if date_time>datetime.datetime.utcnow():
        url=get_gomofs_url_forecast(datetime.datetime.utcnow(),date_time)
    else:
        url=get_gomofs_url(date_time)
    #start download data
    nc=netCDF4.Dataset(str(url))
    gomofs_lons=nc.variables['lon_rho'][:]
    gomofs_lats=nc.variables['lat_rho'][:]
    #gomofs_temp=nc.variables['temp'][0][0]# JiM added [0][0] on 13 May 2020
    #caculate the index of the nearest four points using a "find_nd" function in Lei Zhao's conversion module   
    target_distance=2*zl.dist(lat1=gomofs_lats[0][0],lon1=gomofs_lons[0][0],lat2=gomofs_lats[0][1],lon2=gomofs_lons[0][1])
    eta_rho,xi_rho=zl.find_nd(target=target_distance,lat=lat,lon=lon,lats=gomofs_lats,lons=gomofs_lons)
    '''
    if dist(lat1=lat,lon1=lon,lat2=gomofs_lats[eta_rho][xi_rho],lon2=gomofs_lons[eta_rho][xi_rho])>mindistance:
        print('THE location is out of range')
        return np.nan
    '''
    temperature=nc.variables['temp'][0][0][eta_rho][xi_rho]
    #temperature=gomofs_temp[0][rho_index][eta_rho][xi_rho]
    #temperature=gomofs_temp[eta_rho][xi_rho]
    return temperature


def gomofs_coordinaterange(lat,lon):
    f1=-0.7490553378867058*lat-lon-40.98355685763821<=0
    f2=-0.5967392371008197*lat-lon-36.300860518805024>=0
    f3=2.695505391925802*lat-lon-188.76889647321198<=0
    f4=2.689125428655328*lat-lon-173.5017523298927>=0
    if f1 and f2 and f3 and f4:
        return True
    else:
        return False