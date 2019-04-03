#Dependencies
import RPi.GPIO as gpio

class gpioPin:
    def __init__(self,pin,out,enabled):

        #Initialize gpio to use broadcomm numberings
        gpio.setmode(gpio.BCM)
        
        #Accept pin and on state
        self.pin = pin
        self.enabled = enabled

        #Initialize pin as input or output
        if(out):
            gpio.setup(self.pin, gpio.OUT)
        else:
            gpio.setup(self.pin, gpio.IN, pull_up_down=gpio.PUD_DOWN)

    def on(self):
        gpio.output(self.pin,gpio.HIGH)
        self.enabled = 1

    def off(self):
        gpio.output(self.pin,gpio.LOW)
        self.enabled = 0

    def toggle(self):
        if(self.enabled):
            self.off()
        else:
            self.on()