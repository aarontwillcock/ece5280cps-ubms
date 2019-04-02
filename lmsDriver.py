#LMS Driver

#Dependencies
import ubmsComms        #Communications
import ubmsUtilities    #packing/unpacking load requests
import ubmsLoad         #Creating loads
import struct           #Packing

#Establish outgoing comm on 127.0.0.1:5218
#Establish incoming comm on 127.0.0.1:5217
bmsComm = ubmsComms.uUDPComm(
            "127.0.0.1",5218,
            "127.0.0.1",5217)

#Create load
load1 = ubmsLoad.uLoad(0,6,0,0.200,10,100)

#Create header
data = struct.pack('i', 1)

#Add body length to message
N = len(vars(load1))
data += struct.pack('i',N)

#Add body to message
data += struct.pack('f'*N,vars(load1).values())

#Send it!
bmsComm.udpSendMsg(data)
