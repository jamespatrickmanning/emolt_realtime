# emolt_realtime
Rock_getmatp.py is the main program runs on Raspberry Pi

Function files requires : li_parse; wifiandpic; func_readgps;hrock


This program downloads raw "lid" from lowell logger "MATp-2W", parses the "lid" file to txt and csv file. Gets summary data as mean temperature ,mean depth, time, time length and sends the data to satellite by AP3 or Rockblock. Sends the raw data to our database.
