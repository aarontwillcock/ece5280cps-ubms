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
r_100 = piGpio.gpioPin(PIPPDefs.DH1_PIN,True,False) # Bypass 100 Ohm resistor
r_10a = piGpio.gpioPin(PIPPDefs.DH2_PIN,True,False) # Bypass 010 Ohm resistor
r_10b = piGpio.gpioPin(PIPPDefs.DH3_PIN,True,False) # Bypass 010 Ohm resistor


#Hardware example:
#res + DHL1 + DHL2 + DHL3 = 0 Ohm
#res + DHL1 + DHL2 = 10 Ohm
#res + DHL1 = 20 Ohm
#res = 120 Ohm

#Setup communications
bmsComm = ubmsComms.uUDPComm(
            PIPPDefs.BMS_IP,    #Send-to IP
            PIPPDefs.BMS_PORT,  #Send-to port
            PIPPDefs.LMS_IP,    #Recv-frm IP
            PIPPDefs.LMS_PORT)  #Recv-frm port

#Create Load Request Arg Sets
#name       =           (Vmin,Vmax,Imin,Imax,releaseTime,duration,deadline,token)
#   Honest but Impossible Loads
#       Voltage
#           Requested Voltage too High
vHiArgs =   (12,24,0,100,0,60,1000, 0xDED1)
#           Requested Voltage too Low
vLoArgs =   ( 0, 2,0,100,0,60,1000, 0xDED2)
#       Current
#           Requested Current too High
iHiArgs =   ( 0, 6,7,100,0,60,1000, 0xDED3)
#   Honest, supplyable loads
#       Fan Load - Starts 10 sec after approval, lasts for 10 seconds
fanLoadArgs =   (0,6,0,0.500,10,120,120, 0x0217)
#   Dishonest (or honest but compromised) loads
#       120 Ohm Resistor Load - starts 30 sec after approval, lasts for 90 sec
resLoadArgs =   (0,6,0,0.045,30,90,90, 0x3770)
#       10 Ohm Resistive load drop (120 ohms above becomes 110 ohms)
#           Starts 45 sec after approval lasts for 15 sec
#           This load claims to not increase current (but will)
res10aDropArgs =    (0,6,0,0,45,15,15, 0xBAAD)
#       10 Ohm Resistive load drop (110 ohms above becomes 100 ohms)
#           Starts 75 sec after approval, lasts for 15 sec
#           This load claims to draw a minimum of 500ma (but only draws ~50)
res10bDropArgs =    (0,6,0.5,0.7,75,15,15, 0xCACA)


#Create dictionary of arguments
loadArgs = {}
#   Impossible loads
loadArgs.update({vHiArgs[7]:vHiArgs})
loadArgs.update({vLoArgs[7]:vLoArgs})
loadArgs.update({iHiArgs[7]:iHiArgs})
#   Honest load
loadArgs.update({fanLoadArgs[7]:fanLoadArgs})
#   Dishonest (or honest and compromised loads)
loadArgs.update({resLoadArgs[7]:resLoadArgs})
loadArgs.update({res10aDropArgs[7]:res10aDropArgs})
loadArgs.update({res10bDropArgs[7]:res10bDropArgs})

#Create a dictionary of hardware (pins)
loadPin = {}
loadPin.update({fanLoadArgs[7]:fanLoadPin})
loadPin.update({resLoadArgs[7]:resLoadPin})
loadPin.update({resLoadArgs[7]:r_100})
loadPin.update({res10aDropArgs[7]:r_10a})
loadPin.update({res10bDropArgs[7]:r_10b})

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
tokenNames.update({0x3770:"Res   "})
tokenNames.update({0xBAAD:"Res10a"})
tokenNames.update({0xCACA:"Res10b"})

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