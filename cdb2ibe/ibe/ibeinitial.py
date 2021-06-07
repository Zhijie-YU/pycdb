import IBE
import warnings

def importinitial():
    #self.baseCoord()
    createSetObj()
    createSecObj()
    createAssignObj()
    createContactObj()
    createInitialConditionObj()

def baseCoord():
    BaseCoordinate = IBE.ActiveDocument.addObject("Definition::Coordinate", "Base", "Base")
    BaseCoordinate.CoordinateType = "Cartesian"
    BaseCoordinate.v1 = IBE.Vector(1.0, 0.0, 0.0)
    BaseCoordinate.v2 = IBE.Vector(0.0, 1.0, 0.0)
    IBE.ActiveDocument.Definition.addObject(BaseCoordinate)
        
def createSetObj():
    # create set object
    obj = IBE.ActiveDocument.addObject("Part::Objects", "Objects")
    obj.Label = "对象"
    #IBE.ActiveDocument.getObject("Definition").Group += [obj]
    
def createSecObj():
    # create section object
    obj = IBE.ActiveDocument.addObject("Part::SectionGroup", "Sections")
    obj.Label = "截面"
    #IBE.ActiveDocument.getObject("Definition").Group += [obj]
    
def createAssignObj():
    # create section assignment object
    obj = IBE.ActiveDocument.addObject("Structure::AssignGroup", "Assign")
    obj.Label = "指定"
    
def createContactObj():
    # create connector and contact object
    obj = IBE.ActiveDocument.addObject("Structure::LinkGroup", "ConnectorAndContact")
    obj.Label = "连接与接触"
    
def createInitialConditionObj():
    # create initial condition object
    obj = IBE.ActiveDocument.addObject("Structure::InitialConditionGroup", "InitialCondition")
    obj.Label = "初始条件"
