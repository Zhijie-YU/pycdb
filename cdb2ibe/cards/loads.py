import numpy as np

class SFE():
    # define surface load 
    type = "SFE"
    
    def __init__(self, eid, fid, label, kval, vals):
        self.eid = eid # element id
        self.fid = fid # face id of this element
        self.label = label # default "PRES"
        # kval: 0/1=>real components; 2=>imaginary components
        # (imaginary components should be ignored)
        self.kval = kval 
        assert len(vals) == 4, vals
        self.vals = vals # val1-val4 corresponding to 4 nodes of this face

    @classmethod
    def add_card(cls, card):
        eid = int(card[1])
        fid = int(card[2])
        label = card[3]
        assert label == "PRES", label
        kval = int(card[4])
        vals = [float(v) for v in card[6:]]
        
        return SFE(eid, fid, label, kval, vals)
    