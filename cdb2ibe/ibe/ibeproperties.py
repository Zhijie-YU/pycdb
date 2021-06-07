import IBE, IBEGui
import warnings, time
import numpy as np
from collections import defaultdict
from cdb2ibe.ibe.ibesets import createESet

def importSection(model, sets, eidsMap):
    # import section
    ssets = sets["section"]
    for _, prop in model.properties.items():
        sectype = prop.sectype
        if sectype == "SHELL":
            importShell(prop, ssets)
        elif sectype == "BEAM":
            importBeam(prop, ssets)
        elif sectype == "LINK":
            importTruss(prop, ssets)
        else:
            warnings.warn("Section type {} unsupported!".format(sectype))
            
    # import beam orientation
    importBeamOrientation(model, eidsMap)            
            
def importShell(prop, ssets):
    secid = prop.secid
    section = "ShellSection"
    # there may exist same names thus str(secid) is added!
    label = prop.props["name"] + str(secid)
    nlayers = prop.props["layers"]
    if len(nlayers) != 1:
        warnings.warn("Multi-layer shell is not allowed for section {}!".format(label))
        return
    if prop.props["offset"] != "MID":
        # offset sections are still imported.
        warnings.warn("Offset is not allowed for shell section {}!".format(label))
        #return
        
    thick = prop.props["layers"][0][0]
    obj = addSection(section, secid, label)
    obj.Thickness = "{} m".format(thick/1000)
    IBE.ActiveDocument.Sections.Group += [obj]
    
    secName = obj.Name
    if secid in ssets:
        secSet = ssets[secid]
        assignSection(secName, secSet, label)
        
def importTruss(prop, ssets):
    secid = prop.secid
    section = "TrussSection"
    label = prop.props["name"] + str(secid)
    area = prop.props["area"]
    obj = addSection(section, secid, label)
    obj.Area = str(area) + " mm^2"
    IBE.ActiveDocument.Sections.Group += [obj]
    
    secName = obj.Name
    if secid in ssets:
        secSet = ssets[secid]
        assignSection(secName, secSet, label)                    

def importBeam(prop, ssets):
    secid = prop.secid
    # for section without name, subtype is used instead thus names may be repeated.
    label = prop.props["name"] + str(secid)
    subtype = prop.props["subtype"]
    values = [v/1000 for v in prop.props["values"]] # from mm to m
    # offset sections are still imported. 
    if prop.props["offset"] != "CENT":
        warnings.warn("Offset is not allowed for beam section {}!".format(label))
        #return
    
    if subtype == "RECT":
        section = "RectangleSection"
        obj = addSection(section, secid, label)
        obj.Width = "{} m".format(values[0])
        obj.Height = "{} m".format(values[1])
    elif subtype == "T":
        section = "TSection"
        obj = addSection(section, secid, label)
        w1, w2, t1, t2 = values
        obj.Width = "{} m".format(w1)
        obj.Height = "{} m".format(w2)
        obj.WidthThickness = "{} m".format(t1)
        obj.HeightThickness = "{} m".format(t2)
    elif subtype in {"CSOLID", "CSOL"}:
        section = "CircleSection"
        obj = addSection(section, secid, label)
        obj.Radius = "{} m".format(values[0])
    elif subtype == "I":
        section = "ISection"
        obj = addSection(section, secid, label)
        w1, w2, w3, t1, t2, t3 = values
        obj.BottomFlangeWidth = "{} m".format(w1)
        obj.TopFlangeWidth = "{} m".format(w2)
        obj.Height = "{} m".format(w3)
        obj.BottomFlangeThickness = "{} m".format(t1)
        obj.TopFlangeThickness = "{} m".format(t2)
        obj.WebWidth = "{} m".format(t3)
    elif subtype == "L":
        section = "LSection"
        obj = addSection(section, secid, label)
        w1, w2, t1, t2 = values
        obj.Width = "{} m".format(w1)
        obj.Height = "{} m".format(w2)
        obj.WidthThickness = "{} m".format(t1)
        obj.HeightThickness = "{} m".format(t2)
    else:
        warnings.warn("Beam section subtype {} unsupported!".format(subtype))
        return
    IBE.ActiveDocument.Sections.Group += [obj]
    
    secName = obj.Name
    if secid in ssets:
        secSet = ssets[secid]
        assignSection(secName, secSet, label)    

def addSection(section, secid, label=None):
    # section: "ShellSection"/"BoxSection"/"CircleSection"/"SurfaceRebarSection"...
    secName = "Section" + str(secid)
    obj = IBE.ActiveDocument.addObject("Part::"+section, secName)
    if label:
        obj.Label = label    
    return obj

def assignSection(secName, secSet, secLabel):
    # assign sections to sets
    num = len(IBE.ActiveDocument.Assign.Group) + 1
    assignSec = "AssignSection" + str(num)
    obj = IBE.ActiveDocument.addObject("Structure::AssignSection", assignSec)
    obj.Label = "指定截面-" + secLabel
    obj.Section = IBE.ActiveDocument.getObject(secName)
    obj.SetReferences = IBE.ActiveDocument.getObject(secSet)
    IBE.ActiveDocument.Assign.Group += [obj]
    
def importBeamOrientation(model, eidsMap):
    beamTypes = {"Beam2", "Beam3"}
    '''
    # boSets: [boSet=>{"Orientation": (x,y,z), "Eids": [eids]}, ...]
    boSets = []
    for bt in beamTypes:
        eids = model._type_to_id_map[bt]
        for eid in eids:
            orientation = computeBeamO(eid, bt, model)
            flag = True
            for boSet in boSets:
                if boSet["Orientation"] == orientation:
                    boSet["Eids"].append(eid)
                    flag = False
            if flag:
                # no same orientation is found
                boSet = {"Orientation": orientation, "Eids": [eid]}
                boSets.append(boSet)
    for i in range(len(boSets)):
        eids = boSets[i]["Eids"]
        orientation = boSets[i]["Orientation"]
        label = "指定截面方向-" + str(i+1)
        assignSectionOrientation(eids, model, eidsMap, orientation, label)
    '''
    # boSets: dict => use orientation: tuple as the keys
    # can combine beam sections with the same orientation
    boSets = defaultdict(list)
    for bt in beamTypes:
        eids = model._type_to_id_map[bt]
        for eid in eids:
            orientation = computeBeamO(eid, bt, model)
            boSets[orientation].append(eid)
    num = 1
    for orientation, eids in boSets.items():
        assignSectionOrientation(eids, model, eidsMap, orientation, num)
        num += 1
            
def assignSectionOrientation(eids, model, eidsMap, orientation, num):
    # assign section orientation to beam elements with the same orientation
    
    anum = len(IBE.ActiveDocument.Assign.Group) + 1
    assignSecO = "BeamOrientation" + str(anum)
    obj = IBE.ActiveDocument.addObject("Structure::BeamOrientation", assignSecO)
    obj.Label = "指定截面方向-" + str(num)
    IBE.ActiveDocument.Assign.Group += [obj]
    obj.Orientation = orientation
    
    #setName = createESet(eids, eidsMap, "ESet-BeamOrientation-"+str(num))
    #t0 = time.perf_counter()
    #obj.SetReferences = IBE.ActiveDocument.getObject(setName)
    #print("指定截面方向： {}".format(time.perf_counter()-t0))
    
    # do not create set can save a lot of time
    eidsLocal = defaultdict(list)
    for eid in eids:
        meshId, eidLocal = eidsMap[eid]
        eidsLocal[meshId].append(eidLocal)
    obj.MeshReferences = (2, [(IBE.ActiveDocument.getObject("mesh"+str(meshId)), False, e) for meshId,e in eidsLocal.items()])

    # make it invisible
    IBEGui.ActiveDocument.getObject(assignSecO).Visibility = False
    
def computeBeamO(eid, bt, model):
    # compute beam local y-axis orientation
    assert bt in {"Beam2", "Beam3"}, bt
    nids = model.elements[eid].nids
    # orientation node
    onid = model.elements[eid].onid
    I = model.nodes[nids[0]].xyz
    J = model.nodes[nids[1]].xyz
    xaxis = J - I
    xaxis = xaxis / np.linalg.norm(xaxis)
    if onid:
        # with orientation node
        K = model.nodes[onid].xyz
        # zaxis here is not the real zaxis since zaxis may not be prependicular to xaxis
        zaxis = K - I
        zaxis = zaxis / np.linalg.norm(zaxis)
        yaxis = np.cross(zaxis, xaxis)
        yaxis = yaxis / np.linalg.norm(yaxis)
    else:
        # without orientation node
        z = np.array([0, 0, 1])
        theta = np.arccos(xaxis @ z)
        if theta <= 1e-4:
            yaxis = np.array([0, 1, 0])
        else:
            a = xaxis[0]
            b = xaxis[1]
            if b == 0:
                yaxis = np.array([0, 1, 0])
            else:
                yx = np.sqrt(1/(1+a**2/b**2))
                yaxis = np.array([yx, -a/b*yx, 0])
    
    return (float(yaxis[0]), float(yaxis[1]), float(yaxis[2]))
        
        
        