from flask import Flask,redirect,url_for, render_template, Response, request
import RPi.GPIO as GPIO          
from time import sleep
from gpiozero import Servo
import serial

app = Flask(__name__)
@app.route('/')
def json():
    return render_template('json_old.html')
 

#background process happening without any refreshing
@app.route('/forward')
def f():
        print("forward")
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        temp1=1
        return "a"

@app.route('/reverse')
def b():
        print("backward")
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.HIGH)
        temp1=0
        return "a"
        

@app.route('/stop')
def s():
        print("stop")
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.LOW)
        return "a"

@app.route('/left')
def l():
        #servo.min()
        servo.min()
        print("left")
        return "a"

@app.route('/right')
def r():
        #servo.max()
        servo.max()
        print("right")
        return "a"

@app.route("/dir",methods=['POST','GET'])
def ref():
    message = request.get_json(force=True)
    direction = message['direction']
    direction-=90
    if direction<0:
        direction+=360
    if isinstance(direction, float):
     f = open("dir.txt", "w")
     f.write(str(direction))
     print(direction)
    return "a"

@app.route("/gps",methods=['POST','GET'])
def gps():
    message = request.get_json(force=True)
    lat = message['lat']
    longg = message['long']
    print(str(lat)+" "+str(longg))
    return "a"


if __name__ == "__main__":
	app.run(host='0.0.0.0', debug=True)

