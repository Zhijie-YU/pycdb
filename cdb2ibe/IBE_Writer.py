from collections import defaultdict
import os
import numpy as np
import warnings
import IBE

from cdb2ibe.ibe.ibemesh import importMesh
from cdb2ibe.ibe.ibesets import importSet
from cdb2ibe.ibe.ibematerials import importMat
from cdb2ibe.ibe.ibeconstraints import importConstraint
from cdb2ibe.ibe.ibeproperties import importSection

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
        #self.baseCoord()
        self.createSetObj()
        self.createSecObj()
        
        nidsMap, eidsMap = importMesh(self.model)
        importSet(self.model, nidsMap, eidsMap)
        importMat(self.model)
        importSection(self.model)

        print("========== Cdb import finished.")
        
    def baseCoord(self):
        BaseCoordinate = IBE.ActiveDocument.addObject("Definition::Coordinate", "Base", "Base")
        BaseCoordinate.CoordinateType = "Cartesian"
        BaseCoordinate.v1 = IBE.Vector(1.0, 0.0, 0.0)
        BaseCoordinate.v2 = IBE.Vector(0.0, 1.0, 0.0)
        IBE.ActiveDocument.Definition.addObject(BaseCoordinate)
        
    def createSetObj(self):
        # create set object
        obj = IBE.ActiveDocument.addObject("Part::Objects", "Objects")
        obj.Label = "对象"
        IBE.ActiveDocument.getObject("Definition").Group += [obj]
        
    def createSecObj(self):
        # create section object
        obj = IBE.ActiveDocument.addObject("Part::SectionGroup", "Sections")
        obj.Label = "截面"
        IBE.ActiveDocument.getObject("Definition").Group += [obj]
