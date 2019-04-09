#BMS Driver

#Dependencies
import ubmsComms        #Communications
import ubmsUtilities    #packing/unpacking load requests
import ubmsLoad         #Handling load requests
import ubmsSupply       #Modeling battery
<<<<<<< HEAD
import piGpio           #Interrupt Handling, polarity detection
=======
>>>>>>> e88ba93eb52cb017908453fed87c269889fefae5

#Establish outgoing comm on 127.0.0.1:5217
#Establish incoming comm on 127.0.0.1:5218
bmsComm = ubmsComms.uUDPComm(
            "127.0.0.1",5217,
            "127.0.0.1",5218)

#Tell LMS we are online
bmsComm.udpSendMsg("BMS Online")

#Initialize our own battery
batt = ubmsSupply.uBatt(4.8,1,1200)

<<<<<<< HEAD
#Setup interrupt handling
def printIsr():
    print("ISR!")

coulombCounter = piGpio.gpioPin(13,False,False)
coulombCounter.createInterrupt(True,printIsr,10)

=======
>>>>>>> e88ba93eb52cb017908453fed87c269889fefae5
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