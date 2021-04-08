from cdb2ibe.CDB_Reader import cdbReader
import warnings
import time

'''
import sys
sys.path.append("E:/ansys_converter/Code")
import importcdb
importcdb.main()
'''

def main():
    #warnings.filterwarnings("ignore")
    ts = time.time()
    
    #cdbPath = "E:/ansys_converter/Test_cases/CDB2IBE-CASE-186.cdb"
    #cdbPath = "E:/ansys_converter/Test_cases/CDB2IBE-CASE-temp.cdb"
    #cdbPath = "E:/ansys_converter/Test_cases/solid-shell-beam-link-fluid.cdb"
    #cdbPath = "E:/ansys_converter/Test_cases/solid185-prism.cdb"
    #cdbPath = "E:/ansys_converter/Test_cases/solid185-tetra.cdb"
    cdbPath = "E:/ansys_converter/Test_cases/27Model_FE.cdb"

    model = cdbReader()
    model.readCDB(cdbPath)
    
    ibeSwitch = 0
    if ibeSwitch:
        from cdb2ibe.IBE_Writer import ibeWriter
        ibe = ibeWriter(cdbPath, model)
        ibe.writeIBE()
    
    t = time.time() - ts
    print("Time elapsed: {} s".format(t))
    
if __name__ == "__main__":
    main()