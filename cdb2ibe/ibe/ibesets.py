# operations related to sets
import IBE
from collections import defaultdict
import warnings
from cdb2ibe.ibe.ibemesh import element_types

def importSet(model, nidsMap, eidsMap):
    # import sets from CMBLOCK
    for _, setCM in model.sets.items():
        stype = setCM.stype
        if stype in {"ELEM", "ELEMENT"}:
            eids = getIds(setCM.ids)
            setName = createESet(eids, eidsMap, setCM.name)
        elif stype == "NODE":
            nids = getIds(setCM.ids)
            setName = createNSet(nids, nidsMap, setCM.name)
        else:
            raise Exception("Set type {} unsupported!".format(stype))
    
    # create specific sets
    matSets = defaultdict(list)
    secSets = defaultdict(list)
    # contactSets: {"170": {rc: [[nids], [nids], ...]},...}
    contactSets = defaultdict(dict)
    # contactAttrs: {"170": {rc: [mid, etid]}, "175": {rc: [mid, etid]}, ...}
    contactAttrs = defaultdict(dict)
    
    for eid, element in model.elements.items():
        etype = model.etypes[element.etid].etype
        if etype in element_types:
            # materials can only be assigned to Simdroid accepted mesh types!!!
            matSets[element.mid].append(eid)
        if etype in {"Beam2", "Truss2", "Beam3", "MITC4"}:
            # SolidShell8 element does not need to be assigned section in Simdroid!!!
            secSets[element.secid].append(eid)
        if etype in {"170", "173", "174", "175"}:
            if element.rc in contactSets[etype]:
                contactSets[etype][element.rc].append(element.nids)
                assert contactAttrs[etype][element.rc] == [element.mid, element.etid]
            else:
                contactSets[etype][element.rc] = [element.nids]
                contactAttrs[etype][element.rc] = [element.mid, element.etid]
    
    # import material sets
    # matSetMap: {mid: set internal name, ...}
    matSetMap = {}
    for mid, eids in matSets.items():
        if mid in model.materials:
            setName = createESet(eids, eidsMap, "ESet-Material"+str(mid))
            matSetMap[mid] = setName
        
    # import section sets        
    # secSetMap: {secid: set internal name, ...}
    secSetMap = {}
    for secid, eids in secSets.items():
        if secid in model.properties:
            secLabel = model.properties[secid].props["name"] + str(secid)
            setName = createESet(eids, eidsMap, "ESet-Section-"+secLabel)
            secSetMap[secid] = setName
        
    # build node to element map
    neMap = buildNEMap(model)
    # import sets of type "175", "170", "173", "174"
    # contactSetMap: {"170": {rc: set internal name, ...}, "175": {}, ...}
    contactSetMap = {}
    for etype, rcsets in contactSets.items():
        contactSetMap[etype] = createRCSets(rcsets, nidsMap, eidsMap, neMap, etype)
    # contactSetMapNew: {rc: {"170": set internal name, "175": set internal name}, ...}
    contactSetMapNew = defaultdict(dict)
    for etype, rcsets in contactSetMap.items():
        for rc, setName in rcsets.items():
            assert etype not in contactSetMapNew[rc], (etype, rc)
            contactSetMapNew[rc][etype] = setName
            
    # import constraint sets
    # conSetMap: {conid: set internal name, ...}
    conSetMap = {}
    for conid, spc in model.spcs.items():
        setName = createNSet(spc.nids, nidsMap, "NSet-Constraint"+str(conid))
        conSetMap[conid] = setName            
    
    sets = {"material": matSetMap,
            "section": secSetMap,
            "contact": (contactSetMapNew, contactAttrs),
            "constraint": conSetMap}

    return sets

def createRCSets(sets, nidsMap, eidsMap, neMap, etype=None):
    # create sets based on real constants
    # sets: dict {rc: [[nids],[],], ...}
    # setMap: dict {rc: set internal name}
    setMap = {}
    for rc, nidsList in sets.items():
        nids = []
        for ns in nidsList:
            assert len(ns) > 0
            if len(ns) == 1:
                nids += ns
        if nids:
            assert len(nidsList) == len(nids)
            setName = createNSet(nids, nidsMap, "NSet-"+etype+"-"+str(rc))
            setMap[rc] = setName
        else:
            setName = createSurfSet(nidsList, nidsMap, eidsMap, neMap, "SSet-"+etype+"-"+str(rc))
            setMap[rc] = setName
    return setMap

def getIds(ids):
    # eg. [1,-3,4] => [1,2,3,4]
    newIds = []
    for i,id in enumerate(ids):
        if id < 0:
            newIds += [ids[i-1]+j+1 for j in range(abs(id)-ids[i-1])]
        else:
            newIds.append(id)
    return newIds

def buildNEMap(model):
    # build node to element map
    # neMap: {nid: [eids]}
    neMap = defaultdict(list)
    for eid, element in model.elements.items():
        if model.etypes[element.etid].etype not in element_types:
            # exclude special elements like contact
            continue
        nids = element.nids
        for nid in nids:
            neMap[nid].append(eid)
    return neMap

def createSurfSet(nidsList, nidsMap, eidsMap, neMap, label=None):
    # nidsList: [[nids], []] each item corresponds to a surface
    # get global eid of each surface
    eidsList = []
    for nids in nidsList:
        eid = set(neMap[nids[0]])
        for nid in nids[1:]:
            eid = eid & set(neMap[nid])
        if len(eid) != 1:
            # warnings.warn("{} is the shared surface of elements {}!".format(nids, eid))
            warnings.warn("Creating surface set: there exists shared surfaces between different elements!")

        # for shared surface, choose the first element as the default eid.
        eidsList.append(list(eid)[0])
    assert len(eidsList) == len(nidsList)
    
    # SurfaceType index for creating surface set in Simdroid
    # 0 = "Line2"
    # 1 = "Line3"
    # 2 = "Tri3"
    # 3 = "Tri6"
    # 4 = "Quad4"
    # 5 = "Quad8"
    # surfType: {len(nids): index, }  !!! not appropriate          
    surfType = {3: 2, 
                6: 3,
                4: 4,
                8: 5,
                }
    
    # surfsLocal: {meshid: [[eidlocal, nidslocal*n, surftype]...]}
    surfsLocal = defaultdict(list)
    for eid, nids in zip(eidsList, nidsList):
        try:
            emeshId, eidLocal = eidsMap[eid]
        except KeyError:
            warnings.warn("Creating surface set: Some elements are not included in current imported mesh!")
            continue
        nidsLocal = []
        for nid in nids:
            nidMap = nidsMap[nid]
            nmMap = {}
            # for shared node between different mesh types: nidMap = [0,12,1,22,...]
            # for nonshared one: nidMap = [0,12]
            for i in range(0, len(nidMap), 2):
                nmMap[nidMap[i]] = nidMap[i+1]
            if emeshId in nmMap:
                nidLocal = nmMap[emeshId]
                nidsLocal.append(nidLocal)
            else:
                raise Exception("Creating surface set: nids and eid are inconsistent!")
                   
        surfsLocal[emeshId].append([eidLocal] + nidsLocal + [surfType[len(nidsLocal)]])
        
    obj = IBE.ActiveDocument.getObject("Objects")
    num = len(obj.Group) + 1
    setName = "meshset" + str(num)
    sSetObj = IBE.ActiveDocument.addObject("Definition::MeshSurface", setName)
    sSetObj.Data = (3, [(IBE.ActiveDocument.getObject("mesh"+str(meshId)), [(surf[-1], surf[1:-1], surf[0]) for surf in surfs]) for meshId, surfs in surfsLocal.items()])
    if label:
        sSetObj.Label = label
    obj.Group += [sSetObj]
    
    return setName           

def createESet(eids, eidsMap, label=None):
    # create element set from global eids
    eidsLocal = defaultdict(list)
    for eid in eids:
        try:
            meshId, eidLocal = eidsMap[eid]
            eidsLocal[meshId].append(eidLocal)
        except KeyError:
            warnings.warn("Creating element set: Some elements are not included in current imported mesh!")
    
    if not eidsLocal:
        # remove empty sets        
        return None
    obj = IBE.ActiveDocument.getObject("Objects")
    num = len(obj.Group) + 1
    setName = "meshset" + str(num)
    eSetObj = IBE.ActiveDocument.addObject("Definition::MeshSet", setName)
    eSetObj.Data = (2, [(IBE.ActiveDocument.getObject("mesh"+str(meshId)), False, e) for meshId,e in eidsLocal.items()])
    if label:
        eSetObj.Label = label
    obj.Group += [eSetObj]
    
    # return internal set name    
    return setName

def createNSet(nids, nidsMap, label=None):
    # create node set from global nids
    nidsLocal = defaultdict(list)
    for nid in nids:
        try:
            # for a shared node, the first meshobj it belongs to is chosen.
            meshId, nidLocal = nidsMap[nid][0], nidsMap[nid][1]
            nidsLocal[meshId].append(nidLocal)
        except KeyError:
            warnings.warn("Creating node set: Some nodes are not included in current imported mesh!")
    if not nidsLocal:
        # remove empty sets
        return None
    obj = IBE.ActiveDocument.getObject("Objects")
    num = len(obj.Group) + 1
    setName = "meshset" + str(num)
    nSetObj = IBE.ActiveDocument.addObject("Definition::MeshSet", setName)
    nSetObj.Data = (1, [(IBE.ActiveDocument.getObject("mesh"+str(meshId)), n) for meshId,n in nidsLocal.items()])
    if label:
        nSetObj.Label = label
    obj.Group += [nSetObj]
    
    return setName  