#BMS Driver

#Dependencies
import ubmsComms        #Communications
import ubmsUtilities    #packing/unpacking load requests
import struct

#Establish outgoing comm on 127.0.0.1:5217
#Establish incoming comm on 127.0.0.1:5218
bmsComm = ubmsComms.uUDPComm(
            "127.0.0.1",5217,
            "127.0.0.1",5218)

#Tell LMS we are online
bmsComm.udpSendMsg("BMS Online")

#Begin Periodic routine
while True:
    #Wait for messages
    pkg, addr = bmsComm.udpRecvMsg()

    #Unpack data
    obj = ubmsUtilities.structToObj(pkg,11)

    #Print data
    print(obj)