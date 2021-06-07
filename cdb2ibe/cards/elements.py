import numpy as np
import warnings

class ELEMENT():
    
    type = 'ELEMENT'  
    
    def __init__(self, mid, etid, rc, secid, cid,
                 bd, smid, eshape, nnode, eid, nids, onid=None):
        self.mid = mid # material id
        self.etid = etid # element type local id
        self.rc = rc # real constant number id
        self.secid = secid # section id (for beam)
        self.cid = cid # coordinate system id
        self.bd = bd # birth(0)/death(1) flag
        self.smid = smid # solid model id
        self.eshape = eshape # element shape flag
        self.nnode = nnode # number of nodes
        self.eid = eid # element id !!
        self.nids = nids # list of node ids of this element
        self.onid = onid # orientation node id for beam2, beam3, ...      
        
    @classmethod
    def add_card(cls, card):
        mid = card[0]
        etid = card[1]
        rc = card[2]
        secid = card[3]
        cid = card[4]
        bd = card[5]
        smid = card[6]
        eshape = card[7]
        nnode = card[8]
        eid = card[10]
        nids = []
        for i in range(nnode):
            nids.append(card[11+i])        

        return ELEMENT(mid, etid, rc, secid, cid, bd, smid, eshape, nnode, eid, nids)
    
class ETYPE():
    # defines element type
    type = "ETYPE"
    
    # recommend: [0,0,0,0,...] use list of keys to represent element type
    key2etype = {
        "185": {
            0: {0: "Hex8"},
            2: {0: "Hex8", 1: "Hex8R", 2: "Hex8ICR"},
        },
        "186": {
            0: {0: "Hex20R"},
            2: {0: "Hex20R", 1: "Hex20"},
        },
        "187": {
            0: {0: "Tet10"},
        },
        "190":{
            0: {0: "SolidShell8"},
        },
        "181":{
            0: {0: "MITC4"},
            3: {2: "MITC4"},
        },
        "188":{
            0: {0: "Beam2"},
        },
        "189":{
            0: {0: "Beam3"},
        },
        "180":{
            0: {0: "Truss2"},
        },
        "80":{
            0: {0: "Hex8Fluid"},
        },
    }
    
    def __init__(self, etid=-1, etype="Hex", keyopts = []):
        self.etid = etid
        # for all special elements which are not included in Simdroid mesh tree,
        # their names (etype) should be digital values like "170"
        self.etype = etype
        # keyopts: [[2,2], [3,2], ...]
        # for special element types like contact, spring...
        self.keyopts = keyopts
        
    def getEType(self, ename, keys):
        # get the specific type of element
        # keys = [[2,2], [3,2], ...]
        # each list corresponds to a keyopt line in keys
        # cannot deal with multiple KEYOPTs for ordinary element types!!!
        if keys == []:
            # default type
            key1, key2 = 0, 0
        else:
            key1, key2 = int(keys[0][0]), int(keys[0][1])
        try:
            etype = self.key2etype[ename][key1][key2]
            assert len(keys) <= 1
        except KeyError:
            etype = ename
            if ename not in {"170", "173", "174", "175", "14"}:
                # MESH200 is auxiliary element.
                warnings.warn("Element type {} unrecognized!".format(ename))
                
        return etype       

    @classmethod
    def add_card(cls, card):
        # change "KEYOP" to "KEYOPT"
        card = ["KEYOPT" if s == "KEYOP" else s for s in card]
        
        etid = int(card[1])
        ename = card[2] # str
        
        keys = []
        index = 0
        while "KEYOPT" in card[index:]:
            index = card.index("KEYOPT", index)
            ketid = int(card[index+1])
            assert ketid == etid, (ketid, etid)
            keys.append([int(card[index+2]), int(card[index+3])])
            index += 1
        
        etype = cls().getEType(ename, keys)
        
        return ETYPE(etid, etype, keys)