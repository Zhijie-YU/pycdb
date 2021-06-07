import numpy as np

class SET():
    
    type = 'SET'  
    
    def __init__(self, name, stype, num, sid, ids):
        # for negative values in ids:  12, -18 => from 12 to 18(inclusive)
        
        self.name = name # set name/label
        self.stype = stype # set type ("NODE"/"ELEMENT")
        self.num = num # number of items
        self.sid = sid # set id
        self.ids = ids # ids      
        
    @classmethod
    def add_card(cls, card):
        name = card[0]
        stype = card[1]
        num = card[2]
        sid = card[3]
        ids = card[4:4+num]

        return SET(name, stype, num, sid, ids)
    
class RCSET():
    # real constant sets
    type = 'RCSET'
    
    def __init__(self, rcsid, num, reals):
        # real constant set id
        self.rcsid = rcsid
        # number of reals
        self.num = num
        self.reals = reals
        
    @classmethod
    def add_card(cls, card):
        rcsid = card[0]
        num = card[1]
        reals = card[2:2+num]
        
        return RCSET(rcsid, num, reals)
        

    