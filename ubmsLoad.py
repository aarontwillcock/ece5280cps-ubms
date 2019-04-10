#Load request class for modeling an energy request from the BMS
class uLoad:
    def __init__(self,args):
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

#Load request template for LMS to request supply
class uLoadReq:

    def __init__(self,args):
        
        #Determine number of arguments
        L = len(args)

        #Two arguments (token, uLoadArgs)
        if(L==2):
            self.token = args[0]
            self.__dict__.update(vars(args[1]))
        elif(L==12):
            self.token = args[L]
            load = uLoad(args[:L])
            self.__dict__.update(vars(load))

#Reply template for BMS to accept / reject load request
class uLoadReqReply:
    def __init__(self,args):
        
        #Determine number of arguments
        L = len(args)

        if(L == 2):
            self.token  = args[1]
            self.supplyError = args[0]

