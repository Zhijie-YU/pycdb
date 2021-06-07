import numpy as np
from collections import defaultdict
import warnings

from cdb2ibe.cards.utils import transfer

class SECTION():
    # define section properties (for beam, shell, pipe...)
    type = "SECTION"
    
    def __init__(self, secid=-1, sectype=None, props={}):
        self.secid = secid
        self.sectype = sectype
        # props
        self.props = props

    @classmethod
    def add_card(cls, card):
        data = defaultdict(list)
        keys = {"SECTYPE", "SECDATA", "SECCONTROL", "SECOFFSET", "SECBLOCK"}
        line = []
        oldKey = None
        for s in card:
            if s in keys:
                if oldKey:
                    data[oldKey].append(line)
                    line = []
                oldKey = s
            else:
                line.append(s)
        data[oldKey].append(line)
        # data: {key: list of list [[], [], []], ...}
        
        secid, sectype, props = cls().parseSec(data)
        return SECTION(secid, sectype, props)

    def parseSec(self, data):
        # data: dict (list of lists) => mainly deal with multiple SECDATA lines(for REIN)
        # {"SECTYPE": [["11", "BEAM", ...]],
        # "SECDATA: [["31", "490.88",],["31", "490.88"]]"}        
        props = {}
        secid = int(data["SECTYPE"][0][0])
        sectype = data["SECTYPE"][0][1]
        try:
            subtype = data["SECTYPE"][0][2]
        except:
            subtype = None
        try:
            name = data["SECTYPE"][0][3]
        except:
            name = sectype
        
        props["subtype"] = subtype
        props["name"] = name
        
        if sectype == "BEAM":
            self.parseBeam(data, props)
        elif sectype == "SHELL":
            self.parseShell(data, props)
        elif sectype in {"REIN", "REINF"}:
            self.parseRein(data, props)
        elif sectype == "LINK":
            self.parseTruss(data, props)
        else:
            warnings.warn("Section Type {} unsupported!".format(sectype))
        
        return secid, sectype, props
    
    def parseBeam(self, data, props):
        # geometry data for each section
        props["values"] = [float(v) for v in data["SECDATA"][0]]
        # offset: "CENT", "SHRC", "ORGIN", "USER"
        props["offset"] = data["SECOFFSET"][0][0]
        if props["offset"] == "USER":
            props["offsetyz"] = [float(data["SECOFFSET"][0][1]),float(data["SECOFFSET"][0][2])]
        props["control"] = [float(v) for v in data["SECCONTROL"][0][:4]]
        
    def parseTruss(self, data, props):
        # geometry for truss section
        # only area is obtained
        props["area"] = float(data["SECDATA"][0][0])
        
    def parseShell(self, data, props):
        try:
            # offset: "TOP", "MID"(default), "BOT", "USER"
            props["offset"] = data["SECOFFSET"][0][0]
            if props["offset"] == "USER":
                props["offsetx"] = float(data["SECOFFSET"][0][1])

            sblock = data["SECBLOCK"][0]
            nlayer = int(sblock[0])
            layers = []
            for i in range(nlayer):
                # for each layer: thickness, mid, layer orientation angle, num of integration points
                layers.append([float(sblock[4*i+1]), int(sblock[4*i+2]),
                               float(sblock[4*i+3]), int(sblock[4*i+4])])
            props["layers"] = layers
        except:
            props["offset"] = "MID"
            props["layers"] = [[float(v) for v in data["SECDATA"][0]]]

        props["control"] = [float(v) if v else 0 for v in data["SECCONTROL"][0]]
        
    def parseRein(self, data, props):
        # parse a reinforcing section
        fibers = []
        for line in data["SECDATA"]:
            fiber = []
            for s in line:
                fiber.append(transfer(s))
            fibers.append(fiber)
        props["fibers"] = fibers
        props["control"] = [int(v) for v in data["SECCONTROL"][0][:3]]
            
    
            
        
        
                 
    