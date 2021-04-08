import numpy as np

class CORD():
    # define local coordinate systems
    type = "CORD"
    
    def __init__(self, cid=-1, orgin=[0,0,0], rotation=[0,0,0]):
        # can use rotation matrix to transfer
        self.orgin = orgin
        #self.xaxis = 
        #self.zaxis = 
        pass

    @classmethod
    def add_card(cls, card):
        pass
    
    @classmethod
    def getID(cls, card):
        pass
    
    def add_prop(self, card):
        pass
    