# -*- coding: utf-8 -*-
"""
Created on Mon Nov 29 17:59:59 2021

@author: xhx50
"""

import os
import time
import datetime as dt

begin_time= dt.datetime.now()
while True:
    
    dirpath = '/var/www/vhosts/studentdrifters.org/anno_ftp/Matdata'
    past = time.time() - 2*60*60 # 2 hours
    result = []
    for p, ds, fs in os.walk(dirpath):
        for fn in fs:
            filepath = os.path.join(p, fn)
            if os.path.getmtime(filepath) >= past:
                f=open(filepath)
                lines=f.readlines()
                
                result.append(lines[3]+' &nbsp &nbsp &nbsp &nbsp &nbsp '+filepath.split('anno_ftp/')[1]+'\n\n')
    outfile=open('/var/www/vhosts/emolt.org/httpdocs/raw_last.html','w') 
    outfile.write('<html><style>.redtext {color: red;}</style>\n')
    outfile.write('<br><br>Here are the raw data uploaded in last TWO hours \n<br><br>')
    for i in result:
        
        outfile.write('<br><br>'+i+'<br><br>')  
    outfile.close()    
    time.sleep(60)
    if dt.datetime.now()-begin_time>dt.timedelta(seconds=7000):
        break