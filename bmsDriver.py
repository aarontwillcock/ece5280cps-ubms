#BMS Driver

#Dependencies
import ubmsComms

bmsComm = ubmsComms.uUDPComm("127.0.0.1",5005,"127.0.0.1",5005)

bmsComm.udpSendMsg("1")
data, addr = bmsComm.udpRecvMsg()

print(data)