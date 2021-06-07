import IBE
import warnings

#from cdb2ibe.ibe.ibesets import assignMat2Set

def addData(name, label, cname, pname=None, attr=None, data=[]):
    # name: object internal name (should be unique)
    # label: object label (can be the same)
    # cname: object class name (eg. "Materials", "DensityTemPertinence")
    # pname: name of its parent (eg. "BM")
    # attr: name of the attribute
    # data(list of str): eg. ["0 K", "210 Pa", "0.3"]
    
    obj = IBE.ActiveDocument.addObject("Material::"+cname, name)
    obj.Label = label
    if pname:
        IBE.ActiveDocument.getObject(pname).Group += [obj]
    
    if data:
        #command = "IBE.ActiveDocument.getObject(\"{}\").{}={}".format(name, attr, data)
        #exec(command)
        # avoid using exec to save time
        if attr == "Density":
            IBE.ActiveDocument.getObject(name).Density = data
        elif attr == "Isotropic":
            IBE.ActiveDocument.getObject(name).Isotropic = data
        elif attr == "SpecificHeatCapacity":
            IBE.ActiveDocument.getObject(name).SpecificHeatCapacity = data
        elif attr == "ThermalConductivity":
            IBE.ActiveDocument.getObject(name).ThermalConductivity = data
        elif attr == "ExpansionCoefficient":
            IBE.ActiveDocument.getObject(name).ExpansionCoefficient = data
        else:
            warnings.warn("Material property {} unsupported for material {}!".format(attr, name))

def importMat(model, sets):
    # units
    units = {
        "DENS": "*1e12 kg/m^3",
        "EX": "*1e6 Pa",
        "C": "*1e-6 J/(kg*K)",
        "KXX": " W/(m*K)",
        "ALPX": " 1/K",
    }
    for mid, mat in model.materials.items():
        props = mat.props
        #print(props)
        
        # activeDocument: global
        # ActiveDocument: local
        mname = "Material"+str(mid)
        label = "材料"+str(mid)
        cname = "Materials"
        #pname = "Material"
        addData(mname, label, cname)
        
        # assign sets to material
        # materials without sets are removed!
        msets = sets["material"]
        if mat.mid in msets:
            setName = msets[mat.mid]
            IBE.ActiveDocument.getObject(mname).SetReferences = IBE.ActiveDocument.getObject(setName)
        else:
            IBE.ActiveDocument.removeObject(mname)
            continue

        keys = props.keys()
        if "DENS" in keys:
            key = "DENS"
            name0 = "BasicMaterial"+str(10*mid+1)
            label = "基本材料"
            cname = "BasicMaterial"
            pname = mname
            addData(name0, label, cname, pname)
            
            name1 = "Density"+str(10*mid+1)
            label = mname + "_Density"
            cname = "DensityTemPertinence"
            pname = name0
            attr = "Density"
            data = []
            num = int(len(props[key])/2)
            for t in props[key][:num]:
                data.append(str(t)+" K")
            for v in props[key][num:]:
                data.append(str(v)+units[key])
                
            addData(name1, label, cname, pname, attr, data)
            del props[key]
            
        if "EX" in keys and "PRXY" in keys:
            name0 = "LinearElastic"+str(10*mid+1)
            label = "线弹性"
            cname = "SolidLinearElastic"
            pname = mname
            addData(name0, label, cname, pname)
            
            name1 = "Isotropic"+str(10*mid+1)
            label = mname + "_Isotropic"
            cname = "SolidIsotropicTemPertinence"
            pname = name0
            attr = "Isotropic"
            data = []
            num = int(len(props["EX"])/2)
            assert props["EX"][:num] == props["PRXY"][:num]
            for t in props["EX"][:num]:
                data.append(str(t)+" K")
            for v in props["EX"][num:]:
                data.append(str(v)+units["EX"])
            for v in props["PRXY"][num:]:
                data.append(str(v))
                
            addData(name1, label, cname, pname, attr, data)
            
            if "NUXY" in keys:
                assert props["NUXY"] == props["PRXY"]
                del props["NUXY"]
            del props["EX"]
            del props["PRXY"]
            
        if "C" in keys:
            key = "C"
            name0 = "SpecificHeatGroup"+str(10*mid+1)
            label = "比热容组"
            cname = "SpecificHeatGroup"
            pname = mname
            addData(name0, label, cname, pname)
            
            name1 = "SpecificHeat"+str(10*mid+1)
            label = mname + "_SpecificHeat"
            cname = "SpecificHeat"
            pname = name0
            attr = "SpecificHeatCapacity"
            num = int(len(props[key])/2)
            try:
                assert num == 1
            except:
                warnings.warn("Only temperature independent specific heat is allowed!")
            # what is the unit??
            #data = "\"" + str(props[key][1]) + units[key] + "\""
            data = str(props[key][1]) + units[key]
               
            addData(name1, label, cname, pname, attr, data)
            del props[key]
          
        if "KXX" in keys:
            key = "KXX"
            name0 = "ThermalConductivityGroup"+str(10*mid+1)
            label = "导热系数组"
            cname = "ThermalConductivityGroup"
            pname = mname
            addData(name0, label, cname, pname)
            
            name1 = "IsoThermalConductivity"+str(10*mid+1)
            label = mname + "_ThermalConductivity"
            cname = "ThermalConductivityTemPertinence"
            pname = name0
            attr = "ThermalConductivity"
            data = []
            num = int(len(props[key])/2)
            for t in props[key][:num]:
                data.append(str(t)+" K")
            for v in props[key][num:]:
                data.append(str(v)+units[key])
                
            addData(name1, label, cname, pname, attr, data)
            del props[key]
            
        if "ALPX" in keys:
            key = "ALPX"
            name0 = "Expansion"+str(10*mid+1)
            label = "热膨胀"
            cname = "SolidExpansion"
            pname = mname
            addData(name0, label, cname, pname)
            
            name1 = "ExpansionCoefficient"+str(10*mid+1)
            label = mname + "_ExpansionCoefficient"
            cname = "SolidExpansionCoefficientTemPertinence"
            pname = name0
            attr = "ExpansionCoefficient"
            data = []
            num = int(len(props[key])/2)
            for t in props[key][:num]:
                data.append(str(t)+" K")
            for v in props[key][num:]:
                data.append(str(v)+units[key])
                
            addData(name1, label, cname, pname, attr, data)
            del props[key]
            
        if "ALPD" in keys or "BETD" in keys:
            # damping
            name0 = "DampingGroup"+str(10*mid+1)
            label = "阻尼"
            cname = "SolidDampingGroup"
            pname = mname
            addData(name0, label, cname, pname)
            
            name1 = "Damping"+str(10*mid+1)
            label = mname + "_Damping"
            cname = "SolidDamping"
            pname = name0
            
            addData(name1, label, cname, pname)
            
            if "ALPD" in keys:
                key = "ALPD"
                num = int(len(props[key])/2)
                try:
                    assert num == 1
                except:
                    warnings.warn("Only temperature independent mass damping is allowed!")
                data = props[key][1]
                IBE.ActiveDocument.getObject(name1).Alpha = data
                del props[key]
            if "BETD" in keys:
                key = "BETD"
                num = int(len(props[key])/2)
                try:
                    assert num == 1
                except:
                    warnings.warn("Only temperature independent stiffness damping is allowed!")
                data = props[key][1]
                IBE.ActiveDocument.getObject(name1).Beta = data
                del props[key]
        
        if props:
            for k in props.keys():
                warnings.warn("Material property {} is not added.".format(k))
                
                

        
        
     

'''
IBE.ActiveDocument.addObject("Material::Materials", "Mat2")
IBE.ActiveDocument.getObject("Mat2").Label = "新材料"
IBE.ActiveDocument.getObject("Material").Group += [IBE.ActiveDocument.getObject("Mat2")]

IBE.ActiveDocument.addObject("Material::BasicMaterial","BM2")
IBE.ActiveDocument.getObject("BM2").Label = '基本材料'
IBE.ActiveDocument.getObject("Mat2").Group = [IBE.ActiveDocument.getObject("BM2")]

IBE.ActiveDocument.addObject("Material::BasicDensity","Den2")
IBE.ActiveDocument.getObject("Den2").Label = "密度"
IBE.ActiveDocument.getObject("BM2").Group += [IBE.ActiveDocument.getObject("Den2")]
IBE.ActiveDocument.getObject("Den2").Density = "233 kg/m^3"

IBE.ActiveDocument.addObject("Material::DensityTemPertinence","Den3")
IBE.ActiveDocument.getObject("Den3").Label = "密度"
IBE.ActiveDocument.getObject("BM2").Group += [IBE.ActiveDocument.getObject("Den3")]
IBE.ActiveDocument.getObject("Den3").Density = ['0 K','10 K','10 kg/m^3','20 kg/m^3']
'''
