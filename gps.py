import serial
import time
import string
import pynmea2
# Picking up and printing GPS lat lng... testing GPS signal

while True:
	port="/dev/ttyAMA0"
	ser=serial.Serial(port, baudrate=9600, timeout=0.5)
	dataout = pynmea2.NMEAStreamReader()
	newdata=ser.readline()
	#print("hola"+str(newdata))
	newdata = str(newdata)
	newdata = newdata[2:len(newdata)-5]
	#print(newdata)
	if newdata[0:6] == "$GPRMC":
		newmsg=pynmea2.parse(newdata)
		lat=newmsg.latitude
		lng=newmsg.longitude
		gps = "Latitude=" + str(lat) + "and Longitude=" + str(lng)
		print(gps)
