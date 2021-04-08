import IBE
import warnings

#from cdb2ibe.ibe.ibesets import assignMat2Set

def addData(name, label, cname, pname, attr=None, data=[]):
    # name: object internal name (should be unique)
    # label: object label (can be the same)
    # cname: object class name (eg. "Materials", "DensityTemPertinence")
    # pname: name of its parent (eg. "BM")
    # attr: name of the attribute
    # data(list of str): eg. ["0 K", "210 Pa", "0.3"]
       
    #IBE.ActiveDocument.addObject("Material::"+cname, name)
    #IBE.ActiveDocument.getObject(name).Label = label
    #IBE.ActiveDocument.getObject(pname).Group += [IBE.ActiveDocument.getObject(name)]
    
    obj = IBE.ActiveDocument.addObject("Material::"+cname, name)
    obj.Label = label
    IBE.ActiveDocument.getObject(pname).Group += [obj]
    
    if data:
        command = "IBE.ActiveDocument.getObject(\"{}\").{}={}".format(name, attr, data)
        exec(command)

def importMat(model):
    for mid, mat in model.materials.items():
        props = mat.props
        #print(props)
        
        # activeDocument: global
        # ActiveDocument: local
        mname = "Material"+str(mid)
        label = "材料"+str(mid)
        cname = "Materials"
        pname = "Material"
        addData(mname, label, cname, pname)

        keys = props.keys()
        if "DENS" in keys:
            name0 = "BasicMaterial"+str(10*mid+1)
            label = "基本材料"
            cname = "BasicMaterial"
            pname = mname
            addData(name0, label, cname, pname)
            
            name1 = "Density"+str(10*mid+1)
            label = "密度"
            cname = "DensityTemPertinence"
            pname = name0
            attr = "Density"
            data = []
            num = int(len(props["DENS"])/2)
            for t in props["DENS"][:num]:
                data.append(str(t)+" K")
            for v in props["DENS"][num:]:
                data.append(str(v)+" kg/m^3")
                
            addData(name1, label, cname, pname, attr, data)
            del props["DENS"]
            
        if "EX" in keys and "PRXY" in keys:
            name0 = "LinearElastic"+str(10*mid+1)
            label = "线弹性"
            cname = "SolidLinearElastic"
            pname = mname
            addData(name0, label, cname, pname)
            
            name1 = "Isotropic"+str(10*mid+1)
            label = "Mat_Isotropic"
            cname = "SolidIsotropicTemPertinence"
            pname = name0
            attr = "Isotropic"
            data = []
            num = int(len(props["EX"])/2)
            assert props["EX"][:num] == props["PRXY"][:num]
            for t in props["EX"][:num]:
                data.append(str(t)+" K")
            for v in props["EX"][num:]:
                data.append(str(v)+" Pa")
            for v in props["PRXY"][num:]:
                data.append(str(v))
                
            addData(name1, label, cname, pname, attr, data)
            
            if "NUXY" in keys:
                assert props["NUXY"] == props["PRXY"]
                del props["NUXY"]
            del props["EX"]
            del props["PRXY"]
        
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
