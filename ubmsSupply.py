#Cell class for modeling cell
class uCell:
    def __init__(self,vRated,mAhRated):
        self.V = vRated
        #1000mA per Ampere. 60*60=3600 seconds per hour.
        #1 mAh * (3600 s / h) * (1 A / 1000 mA) = 3.6 s*A = 3.6 Coulombs
        self.C = mAhRated*3.6

#Battery class for modeling cell configuration
#TODO: Create a language for using brackets and commas to arrange batteries 
class uBatt:
    def __init__(self,cells,configMap):
        self.cells = cells
        self.configMap = configMap