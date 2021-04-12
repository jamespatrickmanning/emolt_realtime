# -*- coding: utf-8 -*-
"""
Created on Mon Jan 25 09:52:12 2021

@author: xavier
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan 22 15:05:45 2020
get rockblock data from studentdrifters.org, and save them.

 #need to modify function read_codes() inputfile1 ,path1='/home/hxu/Downloads/'  to your local path
@author: hxu
"""

from matplotlib.dates import date2num
import time
import pysftp
import os
import sys
import subprocess
from dateutil import parser
import glob
import json
import datetime
import numpy as np
import urllib
from dateutil import parser
def read_codes(): #need to modify inputfile1 ,path1='/home/hxu/Downloads/'  to your local path
  # get id,depth from /data5/jmanning/drift/codes.dat, need to change the path1
  inputfile1="codes_temp.dat"
  #path1="/net/data5/jmanning/drift/"
  path1='/var/www/vhosts/emolt.org/huanxin_ftp/'
  #path1="/var/www/vhosts/studentdrifters.org/httpdocs/posthuanxin/"
  f1=open(path1+inputfile1,'r')
  esn,id,depth,vessel_names=[],[],[],[]
  for line in f1:
  	esn.append(line.split()[0])
  	id.append(line.split()[1])
  	depth.append(line.split()[2]) 
  	vessel_names.append(line.split()[3])
  return esn,id,depth,vessel_names
################################################
link='https://studentdrifters.org/posthuanxin/rockemolt.dat' # here is the address where you download rockblock data
#f_output=open('ap3_'+  str(datetime.datetime.now())[:16]+'.dat','w') #open a ouput file,change paths if needed

#daily_output=open('/var/www/vhosts/emolt.org/httpdocs/posthuanxin/daily_emolt.dat','w')
#f_output=open('/var/www/vhosts/emolt.org/httpdocs/rock_emolt.dat','a+')
################################################
#esn2, ide,depth,vessel_names=read_codes()# get the id,depth from /data5/jmanning/drift/codes.dat,
esn,dates,lat,lon,battery,data_send,meandepth,rangedepth,timelen,meantemp,sdeviatemp=[],[],[],[],[],[],[],[],[],[],[], 
date_time,year,month,day,hour,minute,second,yearday=[],[],[],[],[],[],[],[] 
#esn2, ide,depth=read_codes()
newlines=[]

#from urllib.request import urlopen
#f = urlopen(link)
f=open('/var/www/vhosts/emolt.org/httpdocs/posthuanxin/recent_rock_emolt.dat','r')
myfile = f.read()
#print(myfile)
lines=myfile.splitlines()# put everyling into a list
datas,esn,transmit_time=[],[],[]
lines_no_daily=[]
f_output=open('/var/www/vhosts/emolt.org/httpdocs/posthuanxin/recent_rock_emolt.dat','w')
for i in range(len(lines)):
	try:
		#print (len(lines[i]))
		lat1=float(bytearray.fromhex(str(lines[i]).split('data=')[1].split("'")[0]).decode().split(',')[0])
		datas1=bytearray.fromhex(str(lines[i]).split('data=')[1].split("'")[0]).decode()
		esn1=str(lines[i]).split('imei=')[1].split('&')[0]
		transmit_time1=str(lines[i]).split('transmit_time=')[1].split('&iridium')[0]
		dates1=transmit_time1[0:8]+transmit_time1[11:13]+transmit_time1[16:18]+transmit_time1[21:23]
		
		lon1=float(bytearray.fromhex(str(lines[i]).split('data=')[1].split("'")[0]).decode().split(',')[1])
		meandepth1=float(bytearray.fromhex(str(lines[i]).split('data=')[1].split("'")[0]).decode().split(',')[2][0:3]) 
		rangedepth1=float(bytearray.fromhex(str(lines[i]).split('data=')[1].split("'")[0]).decode().split(',')[2][3:6])
		timelen1=float(bytearray.fromhex(str(lines[i]).split('data=')[1].split("'")[0]).decode().split(',')[2][6:9])/1000
		meantemp1=float(bytearray.fromhex(str(lines[i]).split('data=')[1].split("'")[0]).decode().split(',')[2][9:13])/100
		sdeviatemp1=float(bytearray.fromhex(str(lines[i]).split('data=')[1].split("'")[0]).decode().split(',')[2][13:17])/100
		lines_no_daily.append(lines[i])
		date_time1=datetime.datetime.strptime(dates1,"%y-%m-%d%H%M%S" )
		year1=str(date_time1.year)
		month1=str(date_time1.month)
		day1=str(date_time1.day)
		hour1=str(date_time1.hour)
		minute1=str(date_time1.minute)
		second1=str(date_time1.second)
		yearday1=int(date_time1.strftime('%j'))+date_time1.hour/24+date_time1.minute/24./60. # get yearday
		#print (dates1)
		
		lat.append(lat1)
		datas.append(datas1) # format byte data to string and add to "datas" list
		esn.append(esn1)
		transmit_time.append(transmit_time1)


		lon.append(lon1)
		meandepth.append(meandepth1)   
		rangedepth.append(rangedepth1)
		timelen.append(timelen1)
		meantemp.append(meantemp1)
		sdeviatemp.append(sdeviatemp1)
		
		dates.append(dates1)
		date_time.append(date_time1)
		year.append(str(date_time1.year))
		month.append(str(date_time1.month))
		day.append(str(date_time1.day))
		hour.append(str(date_time1.hour))
		minute.append(str(date_time1.minute))
		second.append(str(date_time1.second))
		yearday.append(int(date_time1.strftime('%j'))+date_time1.hour/24+date_time1.minute/24./60.) # get yearday
		
	except:

		continue
esns=set(esn)
esns=list(esns)
lines_recent=[]
for x in range(len(esns)):
    
    for y in range(len(lines_no_daily)):
        
        if esns[x] in lines_no_daily[y]:
            
            writelines=lines_no_daily[y]
    f_output.write(writelines+'\n')
            
            
        
f_output.close()     
    
    			
			
'''

index_idn1=[]
    
for o in range(len(dates)): # to save the file
    if meantemp[o]<30:
          #print (dates[o])
          index_idn1=(np.where(esn[o][-6:]==np.array(ide)))[0][0] # index of the codes_temp file
          id_idn1=esn2[index_idn1] # where is the consecutive time this unit was used
          depth_idn1=-1.0*float(depth[index_idn1]) # make depth negative
          #f_output=open('ap3_'+  str(datetime.datetime.now())[:16]+'.dat', 'w')
          f_output.write(str(id_idn1).rjust(10)+" "+str(esn[o][-7:]).rjust(7)+ " "+str(month[o]).rjust(2)+ " " +
                  str(day[o]).rjust(2)+" " +str(hour[o]).rjust(3)+ " " +str(minute[o]).rjust(3)+ " " )
          f_output.write(("%10.7f") %(yearday[o]))
          #f_output.write(" "+str(lon).rjust(10)+' '+str(lat).rjust(10)+ " " +str(float(depth_idn1)).rjust(4)+ " "
          #        +str(np.nan))
          f_output.write(" "+("%10.5f") %-(lon[o]%100/60+int(lon[o]/100))+' '+("%10.5f") %(lat[o]%100/60+int(lat[o]/100))+' '+str(float(depth_idn1)).rjust(4)+ " "+'nan')
          #f_output.write(" "+str(meandepth).rjust(10)+' '+str(rangedepth).rjust(10)+' '+str(len_day).rjust(10)+  " " +str(mean_temp).rjust(4)+ " "
          #        +str(sdevia_temp)+'\n')            
          f_output.write(" "+str(meandepth[o]).rjust(10)+' '+str(rangedepth[o]).rjust(10)+' '+str(timelen[o]).rjust(10)+  " " +("%6.2f") %(meantemp[o])+ " "
                  +("%6.2f") %(sdeviatemp[o])+("%6.0f") %(int(year[o]))+'\n')  
daily_output.close()          
f_output.close()          
os.system('cat -n /var/www/vhosts/emolt.org/httpdocs/posthuanxin/rock_emolt.dat  | sort -uk2 | sort -nk1 | cut -f2- > /var/www/vhosts/emolt.org/httpdocs/posthuanxin/rock_emolt2.dat')
'''