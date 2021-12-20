print "Please check control_file to modify devices you want to check,ap3 or rock"
file='/home/pi/Desktop/control_file.txt'

f1=open(file,'r')
logger_timerange_lim=int(int(f1.readline().split('  ')[0])/1.5)
logger_pressure_lim=int(f1.readline().split('  ')[0])*1.8  #convert from fathom to meter
transmit=f1.readline().split('  ')[0]
MAC_FILTER=[f1.readline().split('  ')[0]]
boat_type=f1.readline().split('  ')[0]
vessel_num=f1.readline().split('  ')[0]
vessel_name=f1.readline().split('  ')[0]
tilt=f1.readline().split('  ')[0]
try:
        CONNECTION_INTERVAL=int(f1.readline().split('  ')[0])
except:
        pass
try:
        transmitter=f1.readline().split('  ')[0]
except:
        pass
print 'transmitter is '+transmitter
f1.close()
if transmitter<>'ap3':

    import sys
    sys.path.insert(1, '/home/pi/Desktop/mat_modules')
    import hrock
    from hrock import MoExample
    ports='/dev/tty-huanxintrans'
    message='9999.9999,9999.9999'+'cccccccccccccccccccccccct'
    MoExample (ports,message)
    print 'request test is sent'
else:

    import serial
    import time
    ports='tty-huanxintrans'
    ser=serial.Serial('/dev/'+ports, 9600)
    time.sleep(2)
    ser.writelines('\n')
    time.sleep(2)
    ser.writelines('\n')
    time.sleep(2)
    ser.writelines('i\n')
    time.sleep(4)
    ser.writelines('ylb 0000000000000\n')



