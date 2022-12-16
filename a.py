
import RPi.GPIO as GPIO          
from time import sleep
from gpiozero import Servo
import serial

# ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
#ser.in_waiting > 0:line = ser.readline()
    
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
print("\n")
print("The default speed & direction of motor is LOW & Forward.....")
print("rr-run s-stop f-forward b-backward ll-low mm-medium hh-high l-left r-right m-mid e-exit")
print("\n")    

while(1):

    x=input()
    # if ser.in_waiting > 0:
    #     line = str(ser.readline()).split(" ")
    #     try:
    #         dis = int(line[1])
    #     except:
    #         dis=100
    # if(dis<6):
    #     x="s"
    
    if x=='rr':
        print("run")
        if(temp1==1):
         GPIO.output(in1,GPIO.HIGH)
         GPIO.output(in2,GPIO.LOW)
         print("forward")
         x='z'
        else:
         GPIO.output(in1,GPIO.LOW)
         GPIO.output(in2,GPIO.HIGH)
         print("backward")
         x='z'
    
    elif x=='l':
        servo.min()
        print("left")

    elif x=="r":
        servo.max()
        print("right")

    elif x=="m":
        servo.mid()
        print("straight")


    elif x=='s':
        print("stop")
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.LOW)
        x='z'

    elif x=='f':
        print("forward")
        GPIO.output(in1,GPIO.HIGH)
        GPIO.output(in2,GPIO.LOW)
        temp1=1
        x='z'

    elif x=='b':
        print("backward")
        GPIO.output(in1,GPIO.LOW)
        GPIO.output(in2,GPIO.HIGH)
        temp1=0
        x='z'

    elif x=='ll':
        print("low")
        p.ChangeDutyCycle(25)
        x='z'

    elif x=='mm':
        print("medium")
        p.ChangeDutyCycle(50)
        x='z'

    elif x=='hh':
        print("high")
        p.ChangeDutyCycle(75)
        x='z'
     
    
    elif x=='e':
        GPIO.cleanup()
        break
    
    else:
        print("<<<  wrong data  >>>")
        print("please enter the defined data to continue.....")

