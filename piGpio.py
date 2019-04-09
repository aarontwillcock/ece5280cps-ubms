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
<<<<<<< HEAD
        self.out = out
=======
>>>>>>> e88ba93eb52cb017908453fed87c269889fefae5
        if(out):
            gpio.setup(self.pin, gpio.OUT)
        else:
            gpio.setup(self.pin, gpio.IN, pull_up_down=gpio.PUD_DOWN)

    def on(self):
<<<<<<< HEAD
        if(self.out):
            gpio.output(self.pin,gpio.HIGH)
            self.enabled = 1

    def off(self):
        if(self.out):
            gpio.output(self.pin,gpio.LOW)
            self.enabled = 0

    def toggle(self):
        if(self.out):
            if(self.enabled):
                self.off()
            else:
                self.on()

    def createInterrupt(self,rising,fxn, debounceMs):
        if(rising):
            gpio.add_event_detect(self.pin,gpio.RISING,fxn,debounceMs)
        else:
            gpio.add_event_detect(self.pin,gpio.FALLING,fxn,debounceMs)
=======
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
>>>>>>> e88ba93eb52cb017908453fed87c269889fefae5
