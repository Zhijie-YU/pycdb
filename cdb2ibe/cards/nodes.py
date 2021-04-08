import numpy as np

class GRID():
    
    type = 'GRID'  
    
    def __init__(self, nid, entity, line, xyz, rot):
        """
        Creates the GRID card
        """
        self.nid = nid
        self.entity = entity # entity id (geometry info)
        self.line = line # line location (geometry info)
        self.xyz = np.array(xyz, dtype='float64') # coordinates
        assert self.xyz.size == 3, self.xyz.shape
        self.rot = np.array(rot, dtype='float64') # rotation angles        
        
    @classmethod
    def add_card(cls, card):
        nid = card[0]
        entity = card[1]
        line = card[2]
        xyz = [card[3], card[4], card[5]]
        rot = [card[6], card[7], card[8]]

        return GRID(nid, entity, line, xyz, rot)

    