#!/usr/bin/env pybricks-micropython
from pybricks.hubs import EV3Brick
from pybricks.ev3devices import (Motor, TouchSensor, ColorSensor,
                                 InfraredSensor, UltrasonicSensor, GyroSensor)
from pybricks.parameters import Port, Stop, Direction, Button, Color
from pybricks.tools import wait, StopWatch, DataLog
from pybricks.robotics import DriveBase
from pybricks.media.ev3dev import SoundFile, ImageFile
import time

#Initalize the ev3 object
ev3 = EV3Brick()

#Initialize the motors
LEFT_WHEEL = Motor(Port.C)
RIGHT_WHEEL = Motor(Port.A)
#Set the speed of the motors (These values are larger than they were in C because they are measured differently)
SPEED_SLOW = -100
SPEED_FAST = 200
#(-80, 200) Two values that also work for SPEED_SLOW and SPEED_FAST respectively
#Initalize the Sensors
COLOUR_SENSOR = ColorSensor(Port.S1)
ULTRASOUND_SENSOR = UltrasonicSensor(Port.S3)

#The tolerance for the colour sensor to activate
LIGHT_TOLERANCE = 22
lastSeenColour = 0
# 0 - Green
# 1 - Blue


#Returns true if the colour sensor is over a line (The variable shifts the tolerance which is necessary for precision)
def senseColour(offset = 0):
    #Global is used to access the variable outside of the function and not define a new variable
    global lastSeenColour
    #Find the RGB values and the average of all 3
    R,G,B = COLOUR_SENSOR.rgb()
    
    average = (R + G + B) / 3
    #If the average is less than the tolerance, the sensor is over a line
    if average < LIGHT_TOLERANCE + offset:
        #If the Blue value is more than Green + 6 (This is to prevent false positives) set the last seen colour to blue
        if B > G + 6:
            lastSeenColour = 1
        else:
            lastSeenColour = 0
        return True
    return False


#Main loop that follows the line
def mainLoop():    
    while True:
        #If it sees an object within 100mm, stop
        if ULTRASOUND_SENSOR.distance() <= 100:
            LEFT_WHEEL.stop()
            RIGHT_WHEEL.stop()
            return
        #If it sees the line, go right
        if senseColour():
            LEFT_WHEEL.run(SPEED_FAST)
            RIGHT_WHEEL.run(SPEED_SLOW)
        else:#Otherwise go left
            LEFT_WHEEL.run(SPEED_SLOW)
            RIGHT_WHEEL.run(SPEED_FAST)

#What to do when it sees a BLUE obstacle
def handleBlueObstacle():
    LEFT_WHEEL.reset_angle(0)
    #Turn right until it sees the line again
    while senseColour():
        RIGHT_WHEEL.run(-SPEED_FAST)
        LEFT_WHEEL.run(SPEED_FAST)
    while not senseColour():
        RIGHT_WHEEL.run(-SPEED_FAST)
        LEFT_WHEEL.run(SPEED_FAST)
    RIGHT_WHEEL.stop()
    LEFT_WHEEL.stop()

#What to do when it sees a GREEN obstacle
def handleGreenObstacle():
    RIGHT_WHEEL.reset_angle(0)
    #Turn right a small amount to make sure it is on the line
    RIGHT_WHEEL.run_target(SPEED_SLOW, -55)

    #Turn right until it is no longer on the line
    while not senseColour():
        LEFT_WHEEL.run(SPEED_SLOW / 2)
        RIGHT_WHEEL.run(SPEED_FAST / 2)
    #Slowly turn left until it is on the line
    while senseColour(-2):
        LEFT_WHEEL.run(SPEED_FAST / 2)
        RIGHT_WHEEL.run(SPEED_SLOW / 2)
    #Go forward until it is close to the obstacle (40mm)
    while ULTRASOUND_SENSOR.distance()  > 40:
        LEFT_WHEEL.run(SPEED_FAST / 2)
        RIGHT_WHEEL.run(SPEED_FAST / 2)
    #Stop
    LEFT_WHEEL.stop()
    RIGHT_WHEEL.stop()
    #Reset Encoder
    LEFT_WHEEL.reset_angle(0)
    #Run off to the right with the obstacle and then return
    LEFT_WHEEL.run_target(SPEED_FAST, 360)
    LEFT_WHEEL.run_target(SPEED_FAST, 70)

#This is where the code truly starts
#Make sure the motors aren't breaking and then call the line following function
LEFT_WHEEL.stop()
RIGHT_WHEEL.stop()
mainLoop()

#Play a sound of 500Hz for 2 seconds
ev3.speaker.beep(500, 2000)
#After playing a sound check the last seen colour and call the appropriate function
if lastSeenColour == 1:
    handleBlueObstacle()
else:
    handleGreenObstacle()

#Go back to following the line
mainLoop()
