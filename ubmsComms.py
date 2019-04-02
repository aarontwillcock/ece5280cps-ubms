#Dependencies
import socket

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

        #Encode message (required in Python3.x)
        encodedMsg = msg.encode()

        #Send message
        self.sSock.sendto(encodedMsg, (self.sIP,self.sPORT))

    def udpRecvMsg(self):

        #Receive message
        msg, addr = self.lSock.recvfrom(1024)

        #Return values
        return msg, addr