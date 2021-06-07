from collections import defaultdict
import os
import numpy as np
import warnings
import IBE

from cdb2ibe.ibe.ibeinitial import importinitial
from cdb2ibe.ibe.ibemesh import importMesh
from cdb2ibe.ibe.ibesets import importSet
from cdb2ibe.ibe.ibematerials import importMat
from cdb2ibe.ibe.ibeconstraints import importConstraint
from cdb2ibe.ibe.ibeproperties import importSection
from cdb2ibe.ibe.ibecontacts import importContact, importSpring

class ibeWriter():
    def __init__(self, cdbPath, model):
        self.cdbPath = cdbPath
        self.model = model
    
    def writeIBE(self):

        if IBE.ActiveDocument == None:
            IBE.ConfigSet("AnalysisDimension", "3d")
            IBE.ConfigSet("AnalysisDomain", "st")
            doc = IBE.newDocument("NewModel")
            IBE.ActiveDocument = doc
        
        print("========== Writing to Simdroid...")
        # add initial tree nodes
        importinitial()

        nidsMap, eidsMap = importMesh(self.model)

        sets = importSet(self.model, nidsMap, eidsMap)

        importMat(self.model, sets)

        importSection(self.model, sets, eidsMap)

        importContact(self.model, sets)

        importConstraint(self.model, sets)

        #importSpring(self.model, nidsMap)
        
        self.addFreq()
        
        print("========== Cdb import finished.")
        
    def addFreq(self):
        # add frequency analysis
        obj = IBE.ActiveDocument.addObject("Fem::MonitorGroup", "MonitorGroup")
        obj.Label = "监控"
        
        obj = IBE.ActiveDocument.addObject("Structure::FrequencyJob", "JobSetting")
        IBE.ActiveDocument.Structural.Group += [obj]
        obj.Label = "step-1 : 频率分析"
        obj.ModeNumber = 20
        obj.Method = 1
    
