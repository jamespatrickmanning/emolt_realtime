# -*- coding: utf-8 -*-
"""
Created on Fri Nov 13 20:03:17 2020
1, change the path
2, change the content in replace()
@author: Xavier
"""
import glob
for file in (glob.glob("*/*.csv")):
    text = open(file, "r")
    text = ''.join([i for i in text]) \
        .replace("Serial Number,842f\nVessel Number,16\nVP_NUM,410527\nVessel Name,Mary_K", "Serial Number,842f\nVessel Number,17\nVP_NUM,310473\nVessel Name,Linda_Marie")
    x = open(file,"w")
    x.writelines(text)
    x.close()