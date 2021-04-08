import IBE, IBEGui, Fem
from collections import defaultdict
import warnings
import numpy as np

def importMesh(model):
    # import mesh nodes to simdroid
    # sameType: 1(each type of element has a mesh node)/0(all elements in one mesh node)
    sameType = 1
    if sameType:
        eleDict = eleSplit(model)
    else:
        eids = []
        for eid in model.elements:
            eids.append(eid)
        eleDict = {"allmesh": eids}
        
    num = 1
    mesh = []
    for eids in eleDict.values():
        meshAttr = createMesh(eids, model, num, sameType)
        if meshAttr:
            mesh.append(meshAttr)
            num += 1
    # mesh: [(nids, eids), (nids, eids)]
    # build mapping from global nid/eid to local (meshObjIndex, localID)
    # eg. nidsMap = {2: (0, 1), 4:,,,}
    nidsMap = {}
    eidsMap = {}
    for i,meshTuple in enumerate(mesh):
        nids, eids = meshTuple[0], meshTuple[1]
        for j,nid in enumerate(nids):
            if j>0:
                nidsMap[nid] = (i, j)
        for j,eid in enumerate(eids):
            if j>0:
                eidsMap[eid] = (i, j)
    
    IBEGui.SendMsgToActiveView("ViewFit")
    return nidsMap, eidsMap
        
def eleSplit(model):
    # divide the mesh into different mesh nodes according to element type
    eleDict = defaultdict(list) # {"Hex8": [1,2,3], "Hex20": [4,5,6]}
    for eid, element in model.elements.items():
        etid = element.etid
        etype = model.etypes[etid].etype
        eleDict[etype].append(eid)
    return eleDict
           
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
    nids = list(np.unique(nids))
    nids.sort()
    nids = [-1] + nids
    
    mesh = Fem.FemMesh()
    
    for nid in nids[1:]:
        xyz = model.nodes[nid].xyz
        mesh.addNode(xyz[0], xyz[1], xyz[2], nids.index(nid))
    
    etypes = []
    for eid in eids[1:]:
        element = model.elements[eid]
        etid = element.etid
        etype = model.etypes[etid].etype
        etypes.append(etype)
        
        eidLocal = eids.index(eid)
        nidsLocal = []
        n = []
        for nid in element.nids:
            n.append(nids.index(nid))
        # add solid
        if etype in {"Hex8", "Hex8R", "Hex8ICR", "SolidShell8", "Hex8Fluid"}:
            nidsLocal = [n[5], n[6], n[7], n[4], n[1], n[2], n[3], n[0]]
        elif etype in {"Hex20", "Hex20R"}:
            nidsLocal = [n[5], n[6], n[7], n[4], n[1], n[2], n[3], n[0],
                    n[13], n[14], n[15], n[12], n[9], n[10], n[11],
                    n[8], n[17], n[18], n[19], n[16]]
        elif etype in {"Tet4"}:
            nidsLocal = [n[1], n[0], n[2], n[3]]
        elif etype in {"Tet10"}:
            nidsLocal = [n[1], n[0], n[2], n[3], n[4], n[6], n[5], n[8], n[7], n[9]]
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
    IBE.ActiveDocument.Mesh.addObject(meshObj)
    
    # nids=[-1,2,5,...]; eids=[-1,4,6,9,...]
    return (nids, eids)
            
        
            
            