import serial
import time
import string
import pynmea2
import numpy as np
from nn import neural_net
from math import cos, asin, sqrt, pi, atan2

from flask import Flask,redirect,url_for, render_template, Response, request
import RPi.GPIO as GPIO
from time import sleep
from gpiozero import Servo
import serial

servo = Servo(17)

in1 = 24
in2 = 23
en = 27
temp1=1

GPIO.setmode(GPIO.BCM)
GPIO.setup(in1,GPIO.OUT)
GPIO.setup(in2,GPIO.OUT)
GPIO.setup(en,GPIO.OUT)
GPIO.output(in1,GPIO.LOW)
GPIO.output(in2,GPIO.LOW)
p=GPIO.PWM(en,1000)
p.start(25)

GPIO.output(in1,GPIO.HIGH)
GPIO.output(in2,GPIO.LOW)

NUM_SENSORS = 2

dest = [0,0]
cur = [0,0]

cur_north = 0

def stop():
        print("stop")
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.LOW)

def left():
        #servo.min()
        servo.min()
        time.sleep(0.5)
        servo.mid()
        print("left")
        return "a"

def right():
        servo.max()
        time.sleep(0.5)
        servo.mid()
        print("right")
        return "a"


def ref():
    global cur_north
    #message = request.get_json(force=True)
    #direction = message['direction']
    f = open("../dir.txt", "r")
    cn = f.read()
    try:
        cur_north = float(cn)
    except:
        pass
#    print("cur"+str(cur_north))
    return cur_north

def get_cur():
        global cur
        port="/dev/ttyAMA0"
        ser=serial.Serial(port, baudrate=9600, timeout=0.5)
        dataout = pynmea2.NMEAStreamReader()
        newdata=ser.readline()
        newdata = str(newdata)
        
        newdata = newdata[6:len(newdata)-9]
 #       print(newdata)
        if newdata[0:6] == "$GPRMC":
                newmsg=pynmea2.parse(newdata)
                lat=newmsg.latitude
                lng=newmsg.longitude
                cur[0]=lat
                cur[1]=lng

def distance(lat1, lon1, lat2, lon2):
            p = pi/180
            a = 0.5 - cos((lat2-lat1)*p)/2 + cos(lat1*p) * cos(lat2*p) * (1-cos((lon2-lon1)*p))/2
            return 12742 * asin(sqrt(a))

def frame_step(action):
        global dest
        global cur
        global cur_north

        get_cur()
  #      print("cur"+str(cur))
   #     print("dist"+str(dest))
        if action == 0:  # Turn left.
            left()
        elif action == 1:  # Turn right
            right()


        DX = dest[1]-cur[1]
        DY = dest[0]-cur[0]
        rad = atan2(DY, DX)
        deg = rad * (180 / 3.141592)

        #correction_angle = deg + cur_north
        if deg<0:
            deg+=360

        cur_north = ref()
        print("mobile"+str(cur_north)+"co-inclin"+str("deg"))
        correction_angle = abs(deg-cur_north)
        print("correct_angle",end="")
        print(correction_angle)
        #correction_angle = (abs(correction_angle))

        dis = distance(dest[0],dest[1],cur[0],cur[1])

        print("dis"+str(dis))

        normalized_readings = []
        dis=dis*1000
        normalized_readings.append(dis/20)

        normalized_readings.append((correction_angle)) 
        state = np.array([normalized_readings])

        if int(dis)<0.15:
            reward = 200
            stop()
        else:
            if correction_angle>30:
                reward = -1*int(dis/20 )-(int(abs(correction_angle)/2))
                reward = int(reward/10)
            else:
                reward = 20-1*int(dis/20 )-(int(abs(correction_angle)))+30
                reward = int(reward/10)

    #    print(state,end=" ")
        print(reward)

        return reward, state

def play(model):


    # Do nothing to get initial.
    _, state = frame_step((2))

    # Move.
    while True:
        #car_distance += 1

        # Choose action.
        action = (np.argmax(model.predict(state, batch_size=1)))
        #action = int(input())
        # Take action.
        _, state = frame_step(action)


if __name__ == "__main__":
    saved_model = 'saved-models/128-128-64-50000-100000.h5'
    #dest = input("Enter destination coordinates").split(" ")
    #dest[0] = float(dest[0])
    #dest[1] = float(dest[1])
    #dest = [12.966875875743142, 77.71197768093576]
    dest=[12.964224333333334,77.70739866666666]
    model = neural_net(NUM_SENSORS, [128, 128], saved_model)
    get_cur()
    play(model)
    #app.run(host='0.0.0.0', debug=True)
    print("kuch ho ra h")
