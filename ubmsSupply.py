#Dependencies
import ubmsLoad

#Simple battery class
class uBatt:
    def __init__(self,V,C,mAh):
        self.V = V
        self.C = C
        self.mAh = mAh
        self.Imax = (self.mAh / 1000.0) * self.C
        self.mAhConsumed = 0

def isProblemToSupply(batt, loadReq):
    
    #Check for battery voltage
    if(batt.V < loadReq.Vmin or batt.V > loadReq.Vmax):
        return 1

    #Check for min current draw
    if(batt.Imax < loadReq.Imin):
        return 2
    
    #Check for max current draw
    if(batt.Imax < loadReq.Imax):
        return 3

    #Check for min energy draw
    if(batt.mAh < loadReq.Emin):
        return 4

    #Check for max energy draw
    if(batt.mAh < loadReq.Emax):
        return 5

    #All clear
    return 0

    
        

# #Battery class for modeling cell configuration
# #TODO: Create a language for using brackets and commas to arrange batteries 
# class uBatt:
#     def __init__(self,cells,configMap):
#         self.cells = cells
#         self.configMap = configMap