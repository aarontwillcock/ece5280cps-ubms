#BMS Driver

#Dependencies
import ubmsComms        #Communications
import ubmsUtilities    #packing/unpacking load requests
import ubmsLoad         #Handling load requests
import ubmsSupply       #Modeling battery
import piGpio           #Interrupt Handling, polarity detection
import time             #Time tracking
import PIPPDefs         #Pin and IP defines
import time             #Time measurements
import threading        #Threading time interrupt

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

        #Reply accordingly
        loadReqReplyArgs = (loadReq.token,int(supplyError))
        reply = ubmsLoad.uLoadReqReply(loadReqReplyArgs)

        #If load request is fulfillable,
        if(not supplyError):
            
            #Change the release and due time
            loadReq.releaseTime += time.time()

            #Change the due time
            loadReq.deadline += time.time() 

            #Log the accepted load requests
            acceptedLoadReqs.update({loadReq.token : loadReq})

        #Print out reply
        print("Replying with: Token ",reply.token," Supply Error: ", reply.supplyError)

        #Create API call
        apiCall = ubmsComms.createAPIcall(2,reply)

        #Send it!
        bmsComm.udpSendMsg(apiCall)

#Average current calculation
#   Variable Init
now = time.time()
lastSampleTime = now
lastSampleI = batt.mAhConsumed
mA_avg = 0

#   Create periodic timer interrupt
def calcAvgI():

    global lastSampleTime
    global mA_avg

    #Calculate current time
    now = time.time()

    #Calculate change in time since last sample
    dt = now - lastSampleTime

    #Assign last
    lastSampleTime = now

    #Calculate change in mAh since last sample
    dmAh = batt.mAhConsumed - lastSampleI

    #Calculate avg current
    # mA = (mAh / s) * (s/h)
    mA_avg = (dmAh / dt) * (3600/1)
    

#Create Periodic Routine
def periodic():

    global mA_avg

    #Calc current time
    now = time.time()

    #Activate loads if necessary
    for loadReqToken in acceptedLoadReqs:

        #If accepted load request release time is now or later
        if( acceptedLoadReqs.get(loadReqToken).releaseTime >= now
            and acceptedLoadReqs.get(loadReqToken).deadline < now):

            #Flag load as active
            activeLoadReqs.update({loadReqToken:1})
        
        #Else, if accepted load request token exists in the active dictionary
        elif(activeLoadReqs.get(loadReqToken)):

            #Delete its key
            del activeLoadReqs[loadReqToken]

    #Calculate min, max current for all loads
    Imin = 0
    Imax = 0

    for activeLoadReqToken in activeLoadReqs:

        #Sum min/max current
        Imin += acceptedLoadReqs.get(loadReqToken).Imax
        Imax += acceptedLoadReqs.get(loadReqToken).Imin

    print("Imin/Imax")
    print(Imin,"/",Imax)

    #Calculate Current
    calcAvgI()

    #Print avg current
    print(mA_avg)

    #Check for exceeding limits
    #   Find all active jobs
    #   Sum max I for all jobs
    #   If max I of all jobs exceeds mA_avg, reject

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