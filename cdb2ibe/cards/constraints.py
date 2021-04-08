import numpy as np

class D():
    # define general constraints (specified disp, vel, acc...)
    type = "D"
    
    def __init__(self, conid=-1, nid=-1, props={}):
        self.conid = conid # constraint id (= nid)
        self.nid = nid # for possible use when several nodes are involved
        # UX, UY, UZ, ROTX, ROTY, ROTZ
        # for structural analysis, (velocity) VELX, VELY, VELZ
        # (rotational velocity) OMGX, OMGY, OMGZ are also allowed.
        # Note: the latter one will overlap the former one!
        self.props = props 

    @classmethod
    def add_card(cls, card):
        assert len(card) == 5, card
        conid = nid = int(card[1])
        lab = card[2]
        props = {lab: float(card[3])}
        
        return D(conid, nid, props)
    
    @classmethod
    def getID(cls, card):
        assert len(card) == 5, card
        conid = int(card[1])
        return conid
    
    def add_prop(self, card):
        lab = card[2]
        self.props[lab] = float(card[3])
        
class SPC():
    type = "SPC"
    
    def __init__(self, conid, nids=[], props={}):
        self.conid = conid
        self.nids = nids
        self.props = props
        
    def addNid(self, nid):
        self.nids.append(nid)
    