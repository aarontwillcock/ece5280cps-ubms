#Pin Definitions
#   BMS
CC_INT_PIN = 6  #Coulomb Counter Interrupt
CC_POL_PIN = 13 #Coulomb Counter Polarity
CC_CLR_PIN = 19 #Coulomb Counter Interrupt Clear
#   LMS
FAN_PIN = 14    #Fan Control
RES_PIN = 15    #Resistor control
DH1_PIN = 21    #Dishonest load 1 - 330 Ohm
DH2_PIN = 20    #Dishonest load 2 - 010 Ohm
DH3_PIN = 16    #Dishonest load 3 - 010 Ohm

#IP Defines
LMS_IP = "192.168.1.217"
BMS_IP = "192.168.1.218"
SELF_IP = "127.0.0.1"

#Port Defines
LMS_PORT = 5217
BMS_PORT = 5218