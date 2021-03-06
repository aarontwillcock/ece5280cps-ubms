#BMS Driver

#Dependencies
import ubmsComms        #Communications
import ubmsUtilities    #packing/unpacking load requests
import ubmsLoad         #Handling load requests
import ubmsSupply       #Modeling battery
import piGpio           #Interrupt Handling, polarity detection
import time             #Time tracking
import PIPPDefs         #Pin and IP defines
import threading        #Threading time interrupt
import activationChecker#Updates activity status of load requests

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
#   Setup time
now = time.time()
lastSampleTime = now
mA_avg = 0
last_mA_avg = 0

#   Create ISR
def printIsr(self):

    #Establish Globals
    global now
    global lastSampleTime
    global mA_avg
    global last_mA_avg

    #Calculate current time
    now = time.time()

    #Calc mA avg
    #mA = mA * h / (s - s) = mA * h / s 
    last_mA_avg = mA_avg
    mA_avg = (MAH_PER_INT / (now - lastSampleTime)) * (3600/1)

    #Update "last" variables
    lastSampleTime = now

    #Check polarity
    pol = ccPol.get()

    #Clear the interrupt on CC
    ccClr.off()
    ccClr.on()
    
    #Record the mAh consumed
    batt.mAhConsumed += MAH_PER_INT

    #Print mAh consumed
    #print("Consumed ", batt.mAhConsumed, " mAh")

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

#Create dictionary of accepted, active load requests
acceptedLoadReqs = {}
activeLoadReqs = {}

#Create UDP data handler
def handle(data):
    #Extract API call from message
    actionId, body = ubmsComms.extractAPIcall(data)

    #Decode Call
    #   Call is a load request
    if(actionId == 1):
        
        #Decode the request
        loadReq = ubmsLoad.uLoadReq(body)

        #Determine if request can be fulfilled
        supplyError = ubmsSupply.isProblemToSupply(batt,loadReq)

        #Print Supply error
        if(supplyError):
            print(ubmsSupply.getSupplyError(supplyError))

        #Reply accordingly
        loadReqReplyArgs = (loadReq.token,int(supplyError))
        reply = ubmsLoad.uLoadReqReply(loadReqReplyArgs)

        #If load request is fulfillable,
        if(not supplyError):
            
            #Change the release and due time
            loadReq.releaseTime += time.time()
            print("New rel time:", loadReq.releaseTime)

            #Change the due time (recall deadlines are relative offsets)
            loadReq.deadline += loadReq.releaseTime
            print("New deadline:", loadReq.deadline)

            #Log the accepted load requests
            acceptedLoadReqs.update({loadReq.token : loadReq})

        #Print out reply
        print("Replying with: Token ",hex(int(reply.token))," Supply Error: ", reply.supplyError)

        #Create API call
        apiCall = ubmsComms.createAPIcall(2,reply)

        #Send it!
        bmsComm.udpSendMsg(apiCall)

#Print active loads:
def printActiveLoads():
    global acceptedLoadReqs
    global activeLoadReqs

    for token in activeLoadReqs:
        if(activeLoadReqs.get(token)):
            print(hex(int(token)))

#Create Periodic Routine
def periodic():

    global acceptedLoadReqs
    global activeLoadReqs
    global mA_avg
    global last_mA_avg

    #Calc current time
    now = time.time()

    #Check if updated (time-adjusted) current is less than last ISR current
    mA_avg_update = (MAH_PER_INT / (now - lastSampleTime)) * (3600/1)
    if(mA_avg_update < mA_avg):
        last_mA_avg = mA_avg
        mA_avg = mA_avg_update

    #Activate loads if necessary
    acceptedLoadReqs, activeLoadReqs = activationChecker.updateActiveLoads(acceptedLoadReqs,activeLoadReqs,now)

    #Calculate min, max current for all loads
    Imin = 0
    Imax = 0

    for token in activeLoadReqs:

        #If load should be active
        if(activeLoadReqs.get(token)):

            #Sum min/max current
            Imin += acceptedLoadReqs.get(token).Imin
            Imax += acceptedLoadReqs.get(token).Imax

    print(now)
    print("Imin/Imax mAh")
    print(Imin*1000,"/",Imax*1000)
    print("mA Avg: ",mA_avg)

    #Check Boundaries
    if(mA_avg > Imax*1000 and mA_avg >= last_mA_avg):
        print("Hi I - Reject Loads:")
        printActiveLoads()
    
    if(mA_avg < Imin*1000 and mA_avg <= last_mA_avg):
        print("Lo I - Reject Loads:")
        printActiveLoads()

    #TODO:Reject the load

    #Try to receive message
    data, addr = bmsComm.udpRecvMsg(1024)

    #Handle if data returned
    if(not(data == None) and not(addr == None)):
        handle(data)
        print(data)

    #Visually terminate this sample's printout
    print("-----")

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