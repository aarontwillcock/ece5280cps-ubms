#Dependencies
import RPi.GPIO as gpio
import time

#Clean up other programs
gpio.cleanup()

#Initialize gpio to use broadcomm numberings
gpio.setmode(gpio.BCM)

#Setup pin
gpio.setup(13,gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(19,gpio.OUT)

#Disable the clear
gpio.output(19,gpio.HIGH)

while True:
    if(not gpio.input(13)):
        print("Interrupted!")
    
        gpio.output(19,gpio.LOW)
        gpio.output(19,gpio.HIGH)
    
    else:
        print("Pin high (no interrupt)")

    time.sleep(5)
    