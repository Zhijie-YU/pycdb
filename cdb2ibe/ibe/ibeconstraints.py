import IBE
import warnings

def importConstraint(model, sets):
    # consets: {conid: set name, ...}
    consets = sets["constraint"]
    for conid, spc in model.spcs.items():
        obj = IBE.ActiveDocument.addObject("Structure::CommonConstrain", "CConstraint"+str(conid))
        obj.Label = "常规约束"+str(conid)
        IBE.ActiveDocument.InitialCondition.Group += [obj]
        obj.SetReferences = IBE.ActiveDocument.getObject(consets[conid])
        obj.Tx = False
        obj.Ty = False
        obj.Tz = False
        obj.Rx = False
        obj.Ry = False
        obj.Rz = False
        for lab, value in spc.props.items():
            assert value == 0, (lab, value)            
            if lab == "UX":
                obj.Tx = True
            elif lab == "UY":
                obj.Ty = True
            elif lab == "UZ":
                obj.Tz = True
            elif lab == "ROTX":
                obj.Rx = True
            elif lab == "ROTY":
                obj.Ry = True
            elif lab == "ROTZ":
                obj.Rz = True
            else:
                warnings.warn("Constraint type {} unsupported!".format(lab))