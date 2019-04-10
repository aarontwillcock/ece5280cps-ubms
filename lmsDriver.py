#LMS Driver

#Dependencies
import ubmsComms        #Communications
import ubmsUtilities    #packing/unpacking load requests
import ubmsLoad         #Creating loads
import piGpio           #Reading/writing to GPIO

#Pin Definitions
FAN_PIN = 14 #Fan Control
RES_PIN = 15 #Resistor control
DH1_PIN = 21 #Dishonest load 1
DH2_PIN = 20 #Dishonest load 2
DH3_PIN = 16 #Dishonest load 3

#Setup hardware
fanLoad = piGpio.gpioPin(FAN_PIN,True,False)
resLoad = piGpio.gpioPin(RES_PIN,True,False)
dishonestLoad1 = piGpio.gpioPin(DH1_PIN,True,False)
dishonestLoad2 = piGpio.gpioPin(DH2_PIN,True,False)
dishonestLoad3 = piGpio.gpioPin(DH3_PIN,True,False)

#Initialize loads to off
fanLoad.off()
resLoad.off()
dishonestLoad1.off()
dishonestLoad2.off()
dishonestLoad3.off()

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
            BMS_IP,BMS_PORT,    #Send-to address
            LMS_IP,LMS_PORT)    #Recv-from address

#Create load request
#   Token
token = 0xDEAD
#   Load
uLoadArgs = (0,6,0,0.200,100,10,100, token)
loadReq1 = ubmsLoad.uLoadReq(uLoadArgs)

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
    if(not loadReply.supplyError):
        resLoad.on()
        print("load enabled")
