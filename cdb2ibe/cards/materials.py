import numpy as np

class MAT():
    
    type = 'MAT'  
    
    def __init__(self, mid=-1, props={}):
        self.mid = mid # material id
        self.props = props # dictionary for material properties
        # keys: EX, NUXY, PRXY, DENS...
        
    def __getData(self, card, label):
        # get temperature and other properties from input data
        # return a list of floats
        if label == "MPTEMP":
            idLen, idSt = 2, 3 # index of length, stloc
        elif label == "MPDATA":
            idLen, idSt = 2, 5
        else:
            raise Exception("Label {} unrecognized!".format(label))
        
        length = int(card[idLen]) # number of temperatures
        nl = int(np.ceil(length / 3)) # num of mptemp/mpdata lines
        index = -1
        data = []
        for _ in range(nl):
            index = card.index(label, index+1)
            stloc = int(card[index+idSt])
            nv = min(length-stloc+1, 3) # num of temp for each line
            for j in range(nv):
                data.append(float(card[index+idSt+1+j]))
        return data
        
    @classmethod
    def add_card(cls, card):
        # card: a list of strings
        temp = cls().__getData(card, "MPTEMP")
        prop = cls().__getData(card, "MPDATA")
        assert len(temp) == len(prop), (temp, prop)
        
        index = card.index("MPDATA")
        lab = card[index+3]
        mid = int(card[index+4])
        props = {lab: temp + prop}
        
        return MAT(mid, props)
    
    @classmethod
    def getID(cls, card):
        # get id of this instance
        index = card.index("MPDATA")
        mid = int(card[index+4])
        return mid
    
    def add_prop(self, card):
        temp = self.__getData(card, "MPTEMP")
        prop = self.__getData(card, "MPDATA")
        assert len(temp) == len(prop), (temp, prop)
        index = card.index("MPDATA")
        lab = card[index+3]
        self.props[lab] = temp + prop

    