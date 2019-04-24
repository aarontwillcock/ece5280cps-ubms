#Dependencies
import RPi.GPIO as gpio
import time

#Initialize gpio to use broadcomm numberings
gpio.setmode(gpio.BCM)

#Setup pin
gpio.setup(6,gpio.IN, pull_up_down=gpio.PUD_DOWN)
gpio.setup(19,gpio.OUT)

#Disable the clear
gpio.output(19,gpio.HIGH)

try:
    while True:
        if(not gpio.input(6)):
            print("Interrupted!")
        
            gpio.output(19,gpio.LOW)
            gpio.output(19,gpio.HIGH)
        
        else:
            print("Pin high (no interrupt)")

        time.sleep(5)

except KeyboardInterrupt:
        gpio.cleanup()