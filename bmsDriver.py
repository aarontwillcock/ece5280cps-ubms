#BMS Driver

#Dependencies
import ubmsComms        #Communications
import ubmsUtilities    #packing/unpacking load requests
import ubmsLoad         #Handling load requests
import ubmsSupply       #Modeling battery
import piGpio           #Interrupt Handling, polarity detection

#Establish outgoing comm on 127.0.0.1:5217
#Establish incoming comm on 127.0.0.1:5218
bmsComm = ubmsComms.uUDPComm(
            "127.0.0.1",5217,
            "127.0.0.1",5218)

#Tell LMS we are online
bmsComm.udpSendMsg("BMS Online")

#Initialize our own battery
batt = ubmsSupply.uBatt(4.8,1,1200)

#Create GPIO ports
#cc = "Coulomb Counter"
#   Inputs
ccInt = piGpio.gpioPin(13,False,False)  #Interrupt
ccPol = piGpio.gpioPin(6,False,False)   #Polarity
#   Outputs
ccClr = piGpio.gpioPin(26,True,False)   #Clear
ccShd = piGpio.gpioPin(19,True,False)   #Shutdown

#Initialize output values
ccClr.off()
ccShd.off()

#Setup interrupt handling
def printIsr(self):
    
    #Establish count
    count = 0

    #Message that ISR is Triggered
    print("ccInt went low - ISR!")

    #Clear the interrupt on CC
    ccClr.on()
    ccClr.off()

    #Check polarity
    pol = ccPol.get()

    #Increment the count in direction of polarity
    if(pol>0):
        count=count+1
    else:
        count=count-1
    
    ##TODO Create count var
    return

#Catch interrupt on falling edge per
#(https://learn.sparkfun.com/tutorials/ltc4150-coulomb-counter-hookup-guide/all)
ccInt.createInterrupt(False,printIsr,10)

#Begin Periodic routine
while True:
    
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