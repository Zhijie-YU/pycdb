# operations related to sets
import IBE, IBEGui
from collections import defaultdict
import warnings, time

def importContact(model, sets):
    # import contacts
    # contactSets: {rc: {"170": set internal name, "175": set internal name}, ...}
    # contactAttrs: {"170": {rc: [mid, etid]}, "175": {rc: [mid, etid]}, ...}
    contactSets, contactAttrs = sets["contact"]
    for rc, esets in contactSets.items():
        # theoretically each rc corresponds to a contact pair
        assert len(esets) == 2, esets
        assert "170" in esets, esets
        etarget = "170"
        etype = [etype for etype in esets if etype != etarget][0]
        mid, etid = contactAttrs[etype][rc]
        # keyopts: [[2,2], [3,2], ...]
        keyopts = model.etypes[etid].keyopts
        
        cType = ""
        keys = defaultdict(int)
        # for keys not included, the default value is 0
        for keyopt in keyopts:
            keys[keyopt[0]] = keyopt[1]
        if keys[2] == 2 and keys[12] == 5:
            cType = "MPC"
        elif keys[2] == 1 and keys[12] == 5:
            cType = "TIE"                    
                    
        if cType == "MPC":
            obj = IBE.ActiveDocument.addObject("Structure::MPCConnect", "MPCConnect"+str(rc))
            obj.Label = "MPC连接-" + str(rc)
            IBE.ActiveDocument.ConnectorAndContact.Group += [obj]
            assert IBE.ActiveDocument.getObject(esets[etype]).Type == "Node"
            assert IBE.ActiveDocument.getObject(esets[etarget]).Type == "Face"
            obj.SetReferences = IBE.ActiveDocument.getObject(esets[etype])
            obj.SetReferences2 = IBE.ActiveDocument.getObject(esets[etarget])
            obj.LinkType = 0
            obj.SearchType = 0
            influence = model.rcsets[rc].reals[5]
            assert influence < 0, influence
            influence = abs(influence) / 1000
            obj.Influence = str(influence) + " m"
            obj.IsRigid = True
            obj.IsRotationCoupled = False
        elif cType == "TIE":
            obj = IBE.ActiveDocument.addObject("Structure::Tie", "Tie"+str(rc))
            obj.Label = "固定连接-" + str(rc)
            IBE.ActiveDocument.ConnectorAndContact.Group += [obj]
            if IBE.ActiveDocument.getObject(esets[etype]).Type == "Node":
                obj.DiscreteType = "Surface To Node"
            elif IBE.ActiveDocument.getObject(esets[etype]).Type == "Face":
                obj.DiscreteType = "Surface To Surface"
            assert IBE.ActiveDocument.getObject(esets[etarget]).Type == "Face"
            obj.SetReferences = IBE.ActiveDocument.getObject(esets[etarget])
            obj.SetReferences2 = IBE.ActiveDocument.getObject(esets[etype])
            influence = model.rcsets[rc].reals[5]
            assert influence < 0, influence
            influence = abs(influence) / 1000
            obj.Influence = str(influence) + " m"
        else:
            warnings.warn("Contact type unsupported for contact {}!".format(rc))
            
def importSpring(model, nidsMap):
    # import axis spring without damping

    eids = model._type_to_id_map["14"]
    for eid in eids:
        nids = model.elements[eid].nids
        assert len(nids) == 2, eid
        rc = model.elements[eid].rc
        stiff = model.rcsets[rc].reals[0]
        assert model.rcsets[rc].reals[1] == 0 and model.rcsets[rc].reals[2] == 0, rc
        springName = "AxisConnection"+str(eid)
        obj = IBE.ActiveDocument.addObject("Structure::AxisConnection", springName)
        obj.Label = "轴向弹簧-" + str(eid)
        IBE.ActiveDocument.ConnectorAndContact.Group += [obj]
        
        obj.RigidityType = "Constant"
        obj.RigidityValue = "{} N/mm".format(stiff)
        obj.Symmetry = True
        
        nid = nids[0]
        try:
            meshId, nidLocal = nidsMap[nid][0], nidsMap[nid][1]
            obj.MeshReferences = (1, [(IBE.ActiveDocument.getObject("mesh"+str(meshId)), [nidLocal])])
        except KeyError:
            # create geometry node for isolated nodes not in elements
            warnings.warn("There exist isolated spring nodes!")
            nodeName = "Vertex"+str(nid)
            objNode = IBE.ActiveDocument.addObject("Part::PrimitiveVertex", nodeName)
            objNode.Label = "点"+str(nid)
            objNode.Location = IBE.Vector(model.nodes[nid].xyz[0], model.nodes[nid].xyz[1], model.nodes[nid].xyz[2])
            IBEGui.ActiveDocument.getObject(nodeName).Visibility = False
            
            obj.References = objNode
            
        nid = nids[1]
        try:
            meshId, nidLocal = nidsMap[nid][0], nidsMap[nid][1]
            obj.MeshReferences2 = (1, [(IBE.ActiveDocument.getObject("mesh"+str(meshId)), [nidLocal])])
        except KeyError:
            warnings.warn("There exist isolated spring nodes!")
            nodeName = "Vertex"+str(nid)
            objNode = IBE.ActiveDocument.addObject("Part::PrimitiveVertex", nodeName)
            objNode.Label = "点"+str(nid)
            objNode.Location = IBE.Vector(model.nodes[nid].xyz[0], model.nodes[nid].xyz[1], model.nodes[nid].xyz[2])
            IBEGui.ActiveDocument.getObject(nodeName).Visibility = False
            
            obj.References2 = objNode
        
        # make it invisible
        IBEGui.ActiveDocument.getObject(springName).Visibility = False
        
            
    
    
