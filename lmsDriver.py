#LMS Driver

#Dependencies
import ubmsComms        #Communications
import ubmsUtilities    #packing/unpacking load requests
import ubmsLoad         #Creating loads
import piGpio           #Reading/writing to GPIO
import time             #Time tracking
import PIPPDefs         #Pin, IP, and Port defines

#Setup hardware
fanLoad = piGpio.gpioPin(PIPPDefs.FAN_PIN,True,False)
resLoad = piGpio.gpioPin(PIPPDefs.RES_PIN,True,False)
dishonestLoad1 = piGpio.gpioPin(PIPPDefs.DH1_PIN,True,False)
dishonestLoad2 = piGpio.gpioPin(PIPPDefs.DH2_PIN,True,False)
dishonestLoad3 = piGpio.gpioPin(PIPPDefs.DH3_PIN,True,False)

#Create a hardware list
loadList = []
loadList.append(fanLoad)
loadList.append(resLoad)
loadList.append(dishonestLoad1)
loadList.append(dishonestLoad2)
loadList.append(dishonestLoad3)

#Initialize loads to off
for load in loadList:
    load.off()

#Setup communications
bmsComm = ubmsComms.uUDPComm(
            PIPPDefs.BMS_IP,    #Send-to IP
            PIPPDefs.BMS_PORT,  #Send-to port
            PIPPDefs.LMS_IP,    #Recv-frm IP
            PIPPDefs.LMS_PORT)  #Recv-frm port

#Create Load Request Arg Sets
#name       =           (Vmin,Vmax,Imin,Imax,releaseTime,duration,deadline,token)
#Fan Load -         0-6V, 0-500 mA, 10 s from now, for 10 seconds, due 120s from release
fanLoadArgs =           (0,6,0,0.500,10,10,120, 0x0217)

#Resistor Load      0-6V, 0-50mA, 30 s from now, for 60 sec, due 120s from release
resLoadArgs =           (0,6,0,0.050,30,60,120, 0x3770)

#Impossible Load    12-24V, 0-100A, 0s from now, for 60 sec, due 1000s after release
impossibleLoadArgs =    (12,24,0,100,0,60,1000, 0xDEAD)

#DishonestLoads    All are 0-6V, 0-14mA, 60s from now, for 10s, due 100s from release
dishonestLoad1Args =    (0,6,0,0.014,60,10,100, 0xBEEF)     #Load will be drawn too early
dishonestLoad2Args =    (0,6,0,0.014,80,10,100, 0xBAAD)     #Load will be too large
dishonestLoad3Args =    (0,6,0,0.014,100,10,100, 0xCACA)     #Load will be too little

#Create Token-Pin dictionary
tpd = {
        0x0217 : fanLoad,
        0x3770 : resLoad,
        0xBEEF : dishonestLoad1,
        0xBAAD : dishonestLoad2,
        0xCACA : dishonestLoad3
    }

#Create Token-Accepted dictionary
tad = {
        0x0217 : False,
        0x3770 : False,
        0xBEEF : False,
        0xBAAD : False,
        0xCACA : False
    }

#Create arg list
loadArgs = {}
loadArgs.update({fanLoadArgs[7]:fanLoadArgs})
loadArgs.update({resLoadArgs[7]:resLoadArgs})
loadArgs.update({impossibleLoadArgs[7]:impossibleLoadArgs})
loadArgs.update({dishonestLoad1Args[7]:dishonestLoad1Args})
loadArgs.update({dishonestLoad2Args[7]:dishonestLoad2Args})
loadArgs.update({dishonestLoad3Args[7]:dishonestLoad3Args})

#Create Load Requests
loadReqs = {}
for token in loadArgs:
    newLoadReq = ubmsLoad.uLoadReq(loadArgs.get(token))
    loadReqs.update({newLoadReq.token:newLoadReq})

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
            
            #Update dictionary
            tad[loadReply.token] = True

            #Assign actual release time
            loadReqs.get(loadReply.token).releaseTime += time.time()

            #Assign actual deadline
            loadReqs.get(loadReply.token).deadline += time.time()

        else:

            #Print Rejection
            print("Load Req ", hex(int(loadReply.token)), "Rejected!")

#Allow fan if it passed
if(tad[0x0217] == True):
    tpd[0x0217].on()

print("Done!")
##TODO: Execute the dictionary as time passes
