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


    #General UDP Receive
    def udpRecvMsg(self,bufferSize):

        #Receive message
        msg, addr = self.lSock.recvfrom(bufferSize)

        #Return values
        return msg, addr

#API Management
def createAPIcall(actionId,obj):

    #Create header
    data = struct.pack('i', actionId)

    #Add body length to message
    N = len(vars(obj))
    data += struct.pack('i',N)

    #Create value list
    values = obj.getValues()

    #Add body to message
    data += struct.pack('f'*N,*values)

    #Return packaged data
    return data

def extractAPIcall(data):

    #Extract header, body
    header, body = data[:8], data[8:]

    #Unpack header
    actionId, N = struct.unpack('ii',header)

    #Unpack body
    body = struct.unpack('f'*N,body)

    #Return actionId, body
    return actionId, body

