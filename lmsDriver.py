#LMS Driver

#Dependencies
import ubmsComms        #Communications
import ubmsUtilities    #packing/unpacking load requests
import ubmsLoad         #Creating loads
import piGpio           #Reading/writing to GPIO
import time             #Time tracking
import PIPPDefs         #Pin, IP, and Port defines
import activationChecker#Updates activity status of load requests

#Setup hardware
fanLoadPin = piGpio.gpioPin(PIPPDefs.FAN_PIN,True,False)        #Fan
resLoadPin = piGpio.gpioPin(PIPPDefs.RES_PIN,True,False)        # Allow current thru resistors (350 Ohm total)

#Setup communications
bmsComm = ubmsComms.uUDPComm(
            PIPPDefs.BMS_IP,    #Send-to IP
            PIPPDefs.BMS_PORT,  #Send-to port
            PIPPDefs.LMS_IP,    #Recv-frm IP
            PIPPDefs.LMS_PORT)  #Recv-frm port

#Create Load Request Arg Sets
#name       =           (Vmin,Vmax,Imin,Imax,releaseTime,duration,deadline,token)
#   Honest but Impossible Loads
vHiArgs =       (12,24,0.000,0.001,0,60,1000, 0xDED1)   #Voltage too high
vLoArgs =       ( 0, 2,0.000,0.001,0,60,1000, 0xDED2)   #Voltage too low
iHiArgs =       ( 0, 6,7.000,100.0,0,60,1000, 0xDED3)   #Current too high
#   Honest, supplyable loads
fanLoadArgs =   ( 0, 6,0.000,0.500,10,10,10, 0x0217)    #Fan Load
resLoadArgs =   ( 0, 6,0.000,0.045,30,15,15, 0x3770)    #100 Ohm Resistive Load
#   Dishonest loads
badFanLoad1Args=( 0, 6,0.400,0.500,60,15,15, 0xBAD1)    #Claims minimum 400 mA, doesn't draw (undercurrent)
badFanLoad2Args=( 0, 6,0.400,0.500,90,15,15, 0xBAD2)    #Claims max 300 mA, draws more (overcurrent)


#Create dictionary of arguments
loadArgs = {}
#   Impossible loads
loadArgs.update({vHiArgs[7]:vHiArgs})
loadArgs.update({vLoArgs[7]:vLoArgs})
loadArgs.update({iHiArgs[7]:iHiArgs})
#   Honest load
loadArgs.update({fanLoadArgs[7]:fanLoadArgs})
loadArgs.update({resLoadArgs[7]:resLoadArgs})
#   Dishonest (or honest and compromised loads)
loadArgs.update({badFanLoad1Args[7]:badFanLoad1Args})
loadArgs.update({badFanLoad2Args[7]:badFanLoad2Args})

#Create a dictionary of hardware (pins)
loadPin = {}
loadPin.update({fanLoadArgs[7]:fanLoadPin})
loadPin.update({resLoadArgs[7]:resLoadPin})
loadPin.update({badFanLoad1Args[7]:fanLoadPin})
loadPin.update({badFanLoad2Args[7]:fanLoadPin})

#Create dictionary of load requests
loadReqs = {}
for token in loadArgs:
    newLoadReq = ubmsLoad.uLoadReq(loadArgs.get(token))
    loadReqs.update({newLoadReq.token:newLoadReq})

#Create dictionary of accepted load requests
acceptedLoadReqs = {}

#Create dictionary of active load requests
activeLoadReqs = {}

#Create dictionary of load names
tokenNames = {}
tokenNames.update({0x0217:"Fan   "})
tokenNames.update({0x3770:"Res100"})
tokenNames.update({0xBAD1:"FanUnd"})
tokenNames.update({0xBAD2:"FanOvr"})

#Initialize all active entries to 0, False, Not accepted)
for token in loadArgs:
    activeLoadReqs.update({token : 0})

#Create API calls
apiCalls = {}
for token in loadReqs:
    apiCalls.update({token:ubmsComms.createAPIcall(1,loadReqs.get(token))})

#Send API calls (load requests) over UDP
for token in apiCalls:

    #Send API call referenced by token
    bmsComm.udpSendMsg(apiCalls.get(token))

    #Wait for reply
    data, addr = bmsComm.udpRecvMsg(1024)

    #Extract API call from message
    actionId, body = ubmsComms.extractAPIcall(data)

    #Decode Call
    #   Request is a load request reply
    if(actionId == 2):

        #Decode the reply
        loadReply = ubmsLoad.uLoadReqReply(body)

        #Check if load was accepted
        if(not loadReply.supplyError):
            
            #Assign actual release time
            loadReqs.get(loadReply.token).releaseTime += time.time()

            #Assign actual deadline (recall deadlines are relative offsets)
            loadReqs.get(loadReply.token).deadline += loadReqs.get(loadReply.token).releaseTime

            #Update dictionary with accepted load request
            acceptedLoadReqs.update({loadReply.token : loadReqs.get(loadReply.token)})

        else:

            #Print Rejection
            print("Load Req ", hex(int(loadReply.token)), "Rejected!")


#Periodic loop
def periodic():

    global acceptedLoadReqs
    global activeLoadReqs

    #Get current time
    now = time.time()

    #Activate loads if necessary
    acceptedLoadReqs, activeLoadReqs = activationChecker.updateActiveLoads(acceptedLoadReqs,activeLoadReqs,now)

    #Execute the dictionary as time passes
    #   for each active load request token
    for token in activeLoadReqs:

        #If load is active
        if(activeLoadReqs.get(token) and token in loadPin.keys()):

            #Alert user:
            print(hex(int(token)),tokenNames.get(token)," active")

            #Turn on pin (allowing current flow)
            loadPin.get(token).on()

        elif(token in loadPin.keys()):

            #Else, turn off pin
            loadPin.get(token).off()
            print(hex(int(token)),tokenNames.get(token)," inactive")

    print("-----")

    #Wait for next period
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
    for tokens in loadPin:
        loadPin.get(token).off()
    piGpio.cleanup()