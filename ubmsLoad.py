#Load request class for modeling an energy request from the BMS
class uLoad:
    def __init__(self,vmin,vmax,imin,imax,t):
        self.Vmin = vmin
        self.Vmax = vmax
        self.Imin = imin
        self.Imax = imax
        self.Pmin = self.Vmin*self.Imin
        self.Pmax = self.Vmax*self.Imax
        self.duration = t
        self.Emin = self.Pmin*self.duration
        self.Emax = self.Pmax*self.duration
