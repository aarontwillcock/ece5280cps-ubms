#Dependencies
import RPi.GPIO as gpio


#Initialize gpio to use broadcomm numberings
gpio.setmode(gpio.BCM)

#Setup pin
gpio.setup(13,gpio.IN, pull_up_down=gpio.PUD_DOWN)

while True:
    if(gpio.input(13)):
        print("High")
    else:
        print("Low")