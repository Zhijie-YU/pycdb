import IBE
import warnings

def importSection(model):
    # import section
    for _, prop in model.properties.items():
        sectype = prop.sectype
        if sectype == "SHELL":
            importShell(prop)
        elif sectype == "BEAM":
            importBeam(prop)
            
def importShell(prop):
    secid = prop.secid
    section = "ShellSection"
    label = prop.props["name"]
    nlayers = prop.props["layers"]
    if len(nlayers) != 1:
        warnings.warn("Offset is not allowed for shell section {}!".format(label))
        return
    if prop.props["offset"] != "MID":
        # offset sections are still imported.
        warnings.warn("Multi-layer shell is not allowed for section {}".format(label))
        #return
        
    thick = prop.props["layers"][0][0]
    obj = addSection(section, secid, label)
    obj.Thickness = "{} m".format(thick/1000)
    IBE.ActiveDocument.Sections.Group += [obj]             

def importBeam(prop):
    secid = prop.secid
    label = prop.props["name"]
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
        warnings.warn("Beam section type {} unsupported!".format(subtype))
        return
    IBE.ActiveDocument.Sections.Group += [obj]    

def addSection(section, secid, label=None):
    # section: "ShellSection"/"BoxSection"/"CircleSection"/"SurfaceRebarSection"...
    secName = "Section" + str(secid)
    obj = IBE.ActiveDocument.addObject("Part::"+section, secName)
    if label:
        obj.Label = label    
    return obj