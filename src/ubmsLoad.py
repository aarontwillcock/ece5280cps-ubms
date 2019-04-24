#Load request class for modeling an energy request from the BMS
class uLoadReq:
    def __init__(self,args):

        #Determine number of arguments
        L = len(args)

        #7 Arguments
        if(L == 8):
            self.Vmin =         args[0]
            self.Vmax =         args[1]
            self.Imin =         args[2]
            self.Imax =         args[3]
            self.Pmin = self.Vmin*self.Imin
            self.Pmax = self.Vmax*self.Imax
            self.releaseTime =  args[4] 
            self.duration =     args[5]
            self.Emin = self.Pmin*self.duration
            self.Emax = self.Pmax*self.duration
            self.deadline =     args[6]
            self.token =        args[7]
        else:
            self.Vmin =         args[0]
            self.Vmax =         args[1]
            self.Imin =         args[2]
            self.Imax =         args[3]
            self.Pmin =         args[4]
            self.Pmax =         args[5]
            self.releaseTime =  args[6] 
            self.duration =     args[7]
            self.Emin =         args[8]
            self.Emax =         args[9]
            self.deadline =     args[10]
            self.token =        args[11]
    
    def getValues(self):

        #Explicitly order values
        values = (
                    self.Vmin,
                    self.Vmax,
                    self.Imin,
                    self.Imax,
                    self.Pmin,
                    self.Pmax,
                    self.releaseTime,
                    self.duration,
                    self.Emin,
                    self.Emax,
                    self.deadline,
                    self.token,
                )

        return values

#Reply template for BMS to accept / reject load request
class uLoadReqReply:
    def __init__(self,args):
        
        #Determine number of arguments
        L = len(args)

        if(L == 2):
            self.token  = args[0]
            self.supplyError = args[1]

    def getValues(self):
        
        #Explicitly order values
        values = (self.token, self.supplyError)

        return values

