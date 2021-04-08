# operations related to sets
import IBE
from collections import defaultdict
import warnings

def importSet(model, nidsMap, eidsMap):
    # import sets from CMBLOCK
    for _, setCM in model.sets.items():
        stype = setCM.stype
        if stype in {"ELEM", "ELEMENT"}:
            eids = getIds(setCM.ids)
            createESet(eids, eidsMap, setCM.name)
        elif stype == "NODE":
            nids = getIds(setCM.ids)
            createNSet(nids, nidsMap, setCM.name)
        else:
            raise Exception("Set type {} unsupported!".format(stype))

def getIds(ids):
    # eg. [1,-3,4] => [1,2,3,4]
    newIds = []
    for i,id in enumerate(ids):
        if id < 0:
            id = abs(id)
            newIds += [ids[i-1]+j+1 for j in range(abs(id)-ids[i-1])]
        else:
            newIds.append(id)
    return newIds

def createESet(eids, eidsMap, label=None):
    # create element set from global eids
    eidsLocal = defaultdict(list)
    for eid in eids:
        try:
            meshId, eidLocal = eidsMap[eid]
            eidsLocal[meshId].append(eidLocal)
        except KeyError:
            #warnings.warn("Element {} not included in current imported mesh!".format(eid))
            warnings.warn("Creating set: Some elements are not included in current imported mesh!")
    if eidsLocal:
        # remove empty sets        
        obj = IBE.ActiveDocument.getObject("Objects")
        num = len(obj.Group) + 1
        setName = "meshset" + str(num)
        eSetObj = IBE.ActiveDocument.addObject("Definition::MeshSet", setName)
        eSetObj.Data = (2, [(IBE.ActiveDocument.Mesh.Group[meshId], False, e) for meshId,e in eidsLocal.items()])
        if label:
            eSetObj.Label = label
        obj.Group += [eSetObj]    

def createNSet(nids, nidsMap, label=None):
    # create node set from global nids
    nidsLocal = defaultdict(list)
    for nid in nids:
        try:
            meshId, nidLocal = nidsMap[nid]
            nidsLocal[meshId].append(nidLocal)
        except KeyError:
            #warnings.warn("Node {} not included in current imported mesh!".format(nid))
            warnings.warn("Creating set: Some nodes are not included in current imported mesh!")
    if nidsLocal:
        # remove empty sets        
        obj = IBE.ActiveDocument.getObject("Objects")
        num = len(obj.Group) + 1
        setName = "meshset" + str(num)
        nSetObj = IBE.ActiveDocument.addObject("Definition::MeshSet", setName)
        nSetObj.Data = (1, [(IBE.ActiveDocument.Mesh.Group[meshId], n) for meshId,n in nidsLocal.items()])
        if label:
            nSetObj.Label = label
        obj.Group += [nSetObj]

'''
def assignMat2Set(mname, mid, model):
    # create element set and assign material to this set
    eSet = []
    for eid, element in model.elements.items():
        if element.mid == mid:
            eSet.append(eid)
    if eSet:
        # for multiple mesh, zip can be used to create tuples
        meshObj = IBE.ActiveDocument.getObject("mesh1")
        eleSet = [(meshObj, False, eSet)]
        esObj = creatElementSet(eleSet)
        IBE.ActiveDocument.getObject(mname).SetReferences += [esObj]
'''    