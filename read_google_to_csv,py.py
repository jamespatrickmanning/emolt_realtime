# -*- coding: utf-8 -*-
"""
Created on Thu Jul 29 11:24:10 2021

@author: xavier
"""

import csv
import requests
from http.cookiejar import CookieJar
#cj = CookieJar()
#cp = requests.urllib3.HTTPCookieProcessor(cj)
#opener = requests.urllib3.
#cp = requests.HTTPCookieProcessor(cj)
#response = requests.get('https://docs.google.com/spreadsheets/d/1uLhG_q09136lfbFZppU2DU9lzfYh0fJYsxDHUgMB1FM/export?format=csv')
response = requests.get('https://docs.google.com/spreadsheets/d/e/2PACX-1vSzuz56uHqk3-qNVp08VZpBwm3me8hgCvAchRRK2HMdVbIigf-PPaWylV4iRexnGV6oOecOd_hZMB45/pub?gid=1741445972&single=true&output=csv')
assert response.status_code == 200, 'Wrong status code'
response.content.decode('utf-8')
print(response.content)

# open the file in the write mode
with open('csv_file.csv', 'w') as f:
    # create the csv writer
    writer = csv.writer(f)

    # write a row to the csv file
    writer.writerow(response.content)