# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 10:02:42 2021

@author: xavier
"""

import netCDF4
import numpy as np
def get_depth(loni,lati,mindist_allowed):
    # routine to get depth (meters) using vol1 from NGDC
    if lati>=40.:
        url='https://www.ngdc.noaa.gov/thredds/dodsC/crm/crm_vol1.nc'
    else:
        url='https://www.ngdc.noaa.gov/thredds/dodsC/crm/crm_vol2.nc'
    nc = netCDF4.Dataset(url).variables 
    lon=nc['x'][:]
    lat=nc['y'][:]
    xi,yi,min_dist= nearlonlat_zl(lon,lat,loni,lati) 
    if min_dist>mindist_allowed:
      depth=np.nan
    else:
      depth=nc['z'][yi,xi]
    return depth#,min_dist
def nearlonlat_zl(lon,lat,lonp,latp): # needed for the next function get_FVCOM_bottom_temp 
    """ 
    used in "get_depth"
    """ 
    # approximation for small distance 
    cp=np.cos(latp*np.pi/180.) 
    dx=(lon-lonp)*cp
    dy=lat-latp 
    xi=np.argmin(abs(dx)) 
    yi=np.argmin(abs(dy))
    min_dist=111*np.sqrt(dx[xi]**2+dy[yi]**2)
    return xi,yi,min_dist

loni=-69.60232
lati=39.99392
mindist_allowed=5
depth=get_depth(loni,lati,mindist_allowed)
print (depth)