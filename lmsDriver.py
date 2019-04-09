#LMS Driver

#Dependencies
import ubmsComms        #Communications
import ubmsUtilities    #packing/unpacking load requests
import ubmsLoad         #Creating loads
import piGpio           #Reading/writing to GPIO

#Establish hardware control
pin14 = piGpio.gpioPin(14,True,False)

#Establish outgoing comm on 127.0.0.1:5218
#Establish incoming comm on 127.0.0.1:5217
bmsComm = ubmsComms.uUDPComm(
            "127.0.0.1",5218,
            "127.0.0.1",5217)

#Create load
uLoadArgs = (0,6,0,0.200,100,10,100)
load1 = ubmsLoad.uLoad(uLoadArgs)

#Create load request
#   Token
token = 0xDEAD
#   Combing token with load
uLoadReqArgs = (token,load1)
#   Creating load request
loadReq1 = ubmsLoad.uLoadReq(uLoadReqArgs)

#Create API call for UDP
apiCall = ubmsComms.createAPIcall(1,loadReq1)

#Print call
print(apiCall)

#Send it!
bmsComm.udpSendMsg(apiCall)

#Wait for reply
data, addr = bmsComm.udpRecvMsg(1024)#

#Extract API call from message
actionId, body = ubmsComms.extractAPIcall(data)
print(body)

#Decode Call
#   Request is a load request reply
if(actionId == 2):

    #Decode the reply
    loadReply = ubmsLoad.uLoadReqReply(body)

    #Actuate
    if(loadReply.ans):
        pin14.on()
