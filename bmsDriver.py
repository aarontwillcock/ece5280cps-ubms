#BMS Driver

#Dependencies
import ubmsComms        #Communications
import ubmsUtilities    #packing/unpacking load requests
import ubmsLoad         #Handling load requests
import ubmsSupply       #Modeling battery
import piGpio           #Interrupt Handling, polarity detection
#import bmsPinDefs       #Pin definitions for BMS

#Pin Definitions
CC_INT_PIN = 6
CC_POL_PIN = 13
CC_CLR_PIN = 19

#mAh Consumed Definition
#from (https://www.analog.com/media/en/technical-documentation/data-sheets/4150fc.pdf)
#Calc: 1÷(3600×32.55×.05)= 0.000170678 Ah = 0.17067759 mAh
MAH_PER_INT = 0.17067759

#Setup Hardware
#   GPIO ports
#   cc = "Coulomb Counter"
#       Inputs
ccInt = piGpio.gpioPin(CC_INT_PIN,False,False)  #Interrupt
ccPol = piGpio.gpioPin(CC_POL_PIN,False,False)   #Polarity
#       Outputs
ccClr = piGpio.gpioPin(CC_CLR_PIN,True,False)   #Clear
#   Battery Init
batt = ubmsSupply.uBatt(4.8,1,1200)
#       Initialize Coulomb Counter
ccClr.on()

#Setup coulomb count handling
#   Create ISR
def printIsr(self):

    #Message that ISR is Triggered
    print("ccInt went low - ISR!")

    #Check polarity
    pol = ccPol.get()

    #Clear the interrupt on CC
    ccClr.off()
    ccClr.on()
    
    #Record the mAh consumed
    batt.mAhConsumed += MAH_PER_INT

    #Print mAh consumed
    print("Consumed ", batt.mAhConsumed, " mAh")

    #Done
    return

#   Create event detection (interrupt detection) on falling edge per
#(https://learn.sparkfun.com/tutorials/ltc4150-coulomb-counter-hookup-guide/all)
ccInt.createInterrupt(False,printIsr,10)

#IP Addr / Port Defs
#   IPs
LMS_IP = "192.168.1.217"
BMS_IP = "192.168.1.218"
SELF_IP = "127.0.0.1"
#   Ports
LMS_PORT = 5217
BMS_PORT = 5218

#Setup communications
bmsComm = ubmsComms.uUDPComm(
            LMS_IP,LMS_PORT,    #Send-to-address
            BMS_IP,BMS_PORT)    #Recv-from address

#Tell LMS we are online
bmsComm.udpSendMsg("BMS Online")

#Create Periodic Routine
def periodic():
    #Receive message
    data, addr = bmsComm.udpRecvMsg(1024)
    print(data)

    #Extract API call from message
    actionId, body = ubmsComms.extractAPIcall(data)

    #Decode Call
    #   Call is a load request
    if(actionId == 1):
        
        #Decode the request
        loadReq = ubmsLoad.uLoadReq(body)

        #Determine if request can be fulfilled
        isPossible = ubmsSupply.canSupply(batt,loadReq)

        #Reply accordingly
        loadReqReplyArgs = (loadReq.token,int(isPossible))
        reply = ubmsLoad.uLoadReqReply(loadReqReplyArgs)

        #Create API call
        apiCall = ubmsComms.createAPIcall(2,reply)

        #Send it!
        bmsComm.udpSendMsg(apiCall)

#Main loop
#   Try-Except for keyboard interrupts
try:
    #Infinite loop
    while True:

        #Call periodic (main) function
        periodic()

#   If interrupted, cleanup
except KeyboardInterrupt:
    piGpio.cleanup()