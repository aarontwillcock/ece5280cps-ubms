#Dependencies
import RPi.GPIO as gpio
import time


#Initialize gpio to use broadcomm numberings
gpio.setmode(gpio.BCM)

#Setup pin
gpio.setup(13,gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(26,gpio.OUT)
gpio.setup(19,gpio.OUT)

#Turn off shutdown
gpio.output(26,gpio.LOW)

while True:
    if(not gpio.input(13)):
        print("Interrupted!")
    
        gpio.output(19,gpio.HIGH)
        gpio.output(19,gpio.LOW)
    
    else:
        print("Pin high (no interrupt)")

    time.sleep(5)
    