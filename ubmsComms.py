#Dependencies
import socket
import struct

#Communication class for setting up UDP
class uUDPComm:
    def __init__(self,udpIpSend, udpPortSend, udpIpListen, udpPortListen):
        
        #Sending
        self.sIP = udpIpSend
        self.sPORT = udpPortSend

        #Receiving
        self.rIP = udpIpListen
        self.rPORT = udpPortListen

        #Create sending socket
        self.sSock = socket.socket(
                                socket.AF_INET,
                                socket.SOCK_DGRAM
                            )

        #Create listening socket
        self.lSock = socket.socket(
                                    socket.AF_INET,
                                    socket.SOCK_DGRAM
                                )
        
        #Bind socket (listen)
        self.lSock.bind((self.rIP, self.rPORT))

    def udpSendMsg(self,msg):

        #Check if message is a string
        if(isinstance(msg, str)):
            #Encode message (required in Python3.x)
            msg = msg.encode()

        #Send message
        self.sSock.sendto(msg, (self.sIP,self.sPORT))


    def udpRecvMsg(self,bufferSize):

        #Receive message
        msg, addr = self.lSock.recv(bufferSize)

        #Return values
        return msg, addr

    def udpRecvMsgHeader(self):
        return udpRecvMsg(struct.calcsize('i'))

    def udpRecvMsgBodySize(self):
        return udpRecvMsg(struct.calcsize('i'))

#API Management
class ubmsAppendAPIcall:
    def __init__(self,callId,obj):
        self.callId = callId
        self.__dict__.update(vars(obj))