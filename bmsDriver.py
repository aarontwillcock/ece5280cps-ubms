#BMS Driver

#Dependencies
import ubmsComms        #Communications
import ubmsUtilities    #packing/unpacking load requests
import ubmsLoad         #Handling load requests
import ubmsSupply       #Modeling battery
import piGpio           #Interrupt Handling, polarity detection
import time             #Time tracking
import PIPPDefs         #Pin and IP defines

#mAh Consumed Definition
#from (https://www.analog.com/media/en/technical-documentation/data-sheets/4150fc.pdf)
#Calc: 1÷(3600×32.55×.05)= 0.000170678 Ah = 0.17067759 mAh
MAH_PER_INT = 0.17067759

#Setup Hardware
#   GPIO ports
#   cc = "Coulomb Counter"
#       Inputs
ccInt = piGpio.gpioPin(PIPPDefs.CC_INT_PIN,False,False)  #Interrupt
ccPol = piGpio.gpioPin(PIPPDefs.CC_POL_PIN,False,False)  #Polarity
#       Outputs
ccClr = piGpio.gpioPin(PIPPDefs.CC_CLR_PIN,True,False)   #Clear
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

#Setup communications
bmsComm = ubmsComms.uUDPComm(
            PIPPDefs.LMS_IP,     #Send-to IP
            PIPPDefs.LMS_PORT,   #Send-to port
            PIPPDefs.BMS_IP,     #Recv-frm IP
            PIPPDefs.BMS_PORT)   #Recv-frm port
#   Make sending sock blocking
bmsComm.udpSetBlocking(True,True)
#   Make receiving sock NON-blocking
bmsComm.udpSetBlocking(False,False)

#Create UDP data handler
def handle(data):
    #Extract API call from message
    actionId, body = ubmsComms.extractAPIcall(data)

    #Decode Call
    #   Call is a load request
    if(actionId == 1):
        
        #Decode the request
        loadReq = ubmsLoad.uLoadReq(body)

        print(loadReq.getValues())

        #Determine if request can be fulfilled
        supplyError = ubmsSupply.isProblemToSupply(batt,loadReq)

        #Reply accordingly
        loadReqReplyArgs = (loadReq.token,int(supplyError))
        reply = ubmsLoad.uLoadReqReply(loadReqReplyArgs)

        #TODO: Log the accepted load requests

        #Print out reply
        print("Replying with: Token ",reply.token," Supply Error: ", reply.supplyError)

        #Create API call
        apiCall = ubmsComms.createAPIcall(2,reply)

        #Send it!
        bmsComm.udpSendMsg(apiCall)

#Create Periodic Routine
def periodic():

    #Try to receive message
    data, addr = bmsComm.udpRecvMsg(1024)

    #Handle if data returned
    if(not(data == None) and not(addr == None)):
        handle(data)
        print(data)
    
    #TODO: Adjust the min, maximum current draws as time progresses
    #TODO: Enforce current boundaries
    #TODO: Enforce 

    #Sleep
    time.sleep(1)

#Main loop
#   Try-Except for keyboard interrupts
try:
    #Infinite loop
    while True:

        #Call periodic (main) function
        periodic()

#   If interrupted, cleanup GPIO
except KeyboardInterrupt:
    piGpio.cleanup()