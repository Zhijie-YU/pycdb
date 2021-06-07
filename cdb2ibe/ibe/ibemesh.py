import IBE, IBEGui, Fem
from collections import defaultdict
import warnings
import time
import numpy as np

# parsable element types in Simdroid
element_types = {"Hex8", "Hex8R", "Hex8ICR", "SolidShell8", "Hex8Fluid", 
                "Hex20", "Hex20R", "Tet4", "Tet10",
                "MITC4",
                "Beam2", "Truss2", "Beam3",}

def importMesh(model):
    # import mesh nodes to simdroid
    # sameType: 1(each type of element has a mesh node)/0(all elements in one mesh node)
    # element types with different dimensions are not allowed in a single mesh node currently in Simdroid!!!
    # thus sameType = 0 is not recommended.
    sameType = 1
    if sameType:
        eleDict = eleSplit(model)
    else:
        # only import legal elements
        eleDict = eleSplit(model)
        eids = set()
        for typeEids in eleDict.values():
            eids = eids | set(typeEids)
        eleDict = {"allmesh": list(eids)}

    num = 1
    mesh = []
    for _, eids in eleDict.items():
        meshAttr = createMesh(eids, model, num, sameType)
        if meshAttr:
            mesh.append(meshAttr)
            num += 1
    # mesh: [(nids, eids), (nids, eids)]
    # build mapping from global nid/eid to local (meshObjIndex, localID)
    # meshObjIndex should start from 1 thus (i+1)
    ##################
    #### Attention ###
    ##################
    # One nid may corresponds to several meshObjIndex for sharing nodes!!!
    # eg. eidsMap = {2: [0, 1], 4:,,,}
    # eg. for shared node 10: [1, 11, 3, 23] which means this node 10 is shared by 2
    # mesh nodes 1 and 3, with their local nids 11 and 23 respectively.
    
    shareNodes = []
    nidsMap = {}
    eidsMap = {}
    for i,meshTuple in enumerate(mesh):
        nids, eids = meshTuple[0], meshTuple[1]
        for j,nid in enumerate(nids[1:]):
            if nid in nidsMap:
                # shared nodes
                nidsMap[nid] += [i+1, j+1]
                shareNodes.append(nid)
            else:
                nidsMap[nid] = [i+1, j+1]
        for j,eid in enumerate(eids[1:]):
            eidsMap[eid] = [i+1, j+1]
            
    # add shared nodes info
    addShare(shareNodes, nidsMap)    
    
    IBEGui.SendMsgToActiveView("ViewFit")
    
    return nidsMap, eidsMap
        
def eleSplit(model):
    # divide the mesh into different mesh nodes according to element type
    eleDict = defaultdict(list) # {"Hex8": [1,2,3], "Hex20": [4,5,6]}
    for eid, element in model.elements.items():
        etid = element.etid
        etype = model.etypes[etid].etype
        if etype in element_types:
            eleDict[etype].append(eid)
    return eleDict

def addShare(shareNodes, nidsMap):
    shareNodes = list(set(shareNodes))
    # shareDict: {meshId: [[1, 11, meshId, 23], []]}
    # each item contains all the shared nodes of this mesh node
    shareDict = defaultdict(list)
    for nid in shareNodes:
        # assure one node is only shared by two mesh nodes
        # eg. mapIndex = [1, 11, 3, 23]
        mapIndex = nidsMap[nid]
        assert len(mapIndex) == 4, nid
        # mapIndex[-2] refers to the largest mesh node index for this node
        shareDict[mapIndex[-2]].append(mapIndex)
    for meshId, mapIndexes in shareDict.items():
        getMeshObj(meshId).MatchNodes = [(getMeshObj(mapIndex[0]), mapIndex[1], mapIndex[-1]) for mapIndex in mapIndexes]
        
def getMeshObj(meshId):
    # this is based on the assumption that mesh node is named after "mesh+id"!!!
    return IBE.ActiveDocument.getObject("mesh"+str(meshId))
           
def createMesh(eids, model, num, sameType=0):
    # create a single mesh node given global eids list
    # eids: [4,8,9,...] global element ids
    # num: for unique mesh name
    # sameType: whether eids have the same type of element
    
    # global indexes should be transfered to local indexes
    # within a single mesh node
    # local indexes should start from 1 rather than 0 thus "-1" is added
    eids.sort()
    eids = [-1] + eids
    nids = []
    for eid in eids[1:]:
        element = model.elements[eid]
        nids += element.nids
    # !!! change np.unique() to set() greatly reduces the computation time when using .index()!!!
    # nids = list(np.unique(nids))
    nids = list(set(nids))
    nids.sort()
    nids = [-1] + nids  
    mesh = Fem.FemMesh()
    
    # build dict rather than using index to save time !!!
    nidsNew = {}
    for i, nid in enumerate(nids[1:]):
        nidsNew[nid] = i+1
    eidsNew = {}
    for i, eid in enumerate(eids[1:]):
        eidsNew[eid] = i+1

    for nid in nids[1:]:
        xyz = model.nodes[nid].xyz
        #mesh.addNode(xyz[0], xyz[1], xyz[2], nids.index(nid))
        mesh.addNode(xyz[0], xyz[1], xyz[2], nidsNew[nid])

    etypes = []
    for eid in eids[1:]:
        
        element = model.elements[eid]
        etid = element.etid
        etype = model.etypes[etid].etype
        etypes.append(etype)

        #eidLocal = eids.index(eid)
        eidLocal = eidsNew[eid]
        nidsLocal = []
        n = []
        for nid in element.nids:
            #n.append(nids.index(nid))
            n.append(nidsNew[nid])
        # add solid
        if etype in {"Hex8", "Hex8R", "Hex8ICR", "SolidShell8", "Hex8Fluid", 
                     "Hex20", "Hex20R",
                     "Tet4", "Tet10",}:
            nidsLocal = n
        if nidsLocal:
            mesh.addVolume(nidsLocal, eidLocal)
            continue
        # add shell    
        if etype in {"MITC4"}:
            nidsLocal = [n[0], n[1], n[2], n[3]]
        if nidsLocal:
            mesh.addFace(nidsLocal, eidLocal)
            continue
        # add beam
        if etype in {"Beam2", "Truss2"}:
            nidsLocal = [n[0], n[1]]
        elif etype in {"Beam3"}:
            nidsLocal = [n[0], n[2], n[1]]
        if nidsLocal:
            mesh.addEdge(nidsLocal, eidLocal)
            continue
                
        if not nidsLocal:
            warnings.warn("Element type {} unsupported!".format(etype))
            if sameType:
                return

    if not (mesh.EdgeCount or mesh.FaceCount or mesh.VolumeCount):
        # remove mesh nodes without elements
        return    
      
    meshObj = IBE.ActiveDocument.addObject("Fem::ImportMeshObject", "mesh"+str(num))
    if sameType:
        meshObj.Label = etype
    else:
        meshObj.Label = "MESH"
    meshObj.FemMesh = mesh
    meshObj.ElementTypes = etypes

    # nids=[-1,2,5,...]; eids=[-1,4,6,9,...]
    return (nids, eids)
            
        
            
            