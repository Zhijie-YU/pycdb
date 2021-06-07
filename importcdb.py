from cdb2ibe.CDB_Reader import cdbReader
import warnings
import time, cProfile

'''
import sys
sys.path.append("E:/ansys_converter/Code")
import importcdb
importcdb.main("E:/ansys_converter/CDB_docs/Pile-Caps.cdb")

import sys
sys.path.append("E:/ansys_converter/Code")
import importcdb
importcdb.runMain()

fail
import sys
sys.path.append("E:/ansys_converter/Code")
import importcdb
importcdb.main("E:/ansys_converter/CDB_docs/ConRoof-StlRoof-Susdeck.cdb")

success
import sys
sys.path.append("E:/ansys_converter/Code")
import importcdb
importcdb.main("E:/ansys_converter/CDB_docs/ConRoof-StlRoof-Plate-Beam.cdb")

fail
import sys
sys.path.append("E:/ansys_converter/Code")
import importcdb
importcdb.main("E:/ansys_converter/CDB_docs/susdeck-plate-beam.cdb")

import sys
sys.path.append("E:/ansys_converter/Code")
import importcdb
importcdb.main("E:/ansys_converter/CDB_docs/beam-solid.cdb")

import sys
sys.path.append("E:/ansys_converter/Code")
import importcdb
importcdb.main("E:/ansys_converter/CDB_docs/outer-model.cdb")

import sys
sys.path.append("E:/ansys_converter/Code")
import importcdb
importcdb.main("E:/ansys_converter/CDB_docs/CapConWallNew.cdb")

import sys
sys.path.append("E:/ansys_converter/Code")
import importcdb
importcdb.main("E:/ansys_converter/Test_cases/27Model_FE.cdb")
'''

def main(cdbPath=None):
    #cdbPath = "E:/ansys_converter/CDB_docs/Pile-Caps.cdb"
    #cdbPath = "E:/ansys_converter/CDB_docs/ConRoof-StlRoof-Plate-Beam.cdb"
    #cdbPath = "E:/ansys_converter/Test_cases/27Model_FE.cdb"
    
    #warnings.filterwarnings("ignore")
    ts = time.time()

    model = cdbReader()
    model.readCDB(cdbPath)
    print("Time for reading: {} s".format(time.time()-ts))
    
    ibeSwitch = 1
    if ibeSwitch:
        from cdb2ibe.IBE_Writer import ibeWriter
        ibe = ibeWriter(cdbPath, model)
        ibe.writeIBE()
    
    t = time.time() - ts
    print("Total time elapsed: {} s".format(t))
    
def runMain():
    cProfile.run("importcdb.main()")
    
if __name__ == "__main__":
    #cdbPath = "E:/ansys_converter/Test_cases/CDB2IBE-CASE-186.cdb"
    #cdbPath = "E:/ansys_converter/Test_cases/CDB2IBE-CASE-temp.cdb"
    #cdbPath = "E:/ansys_converter/Test_cases/solid-shell-beam-link-fluid.cdb"
    #cdbPath = "E:/ansys_converter/Test_cases/solid185-prism.cdb"
    #cdbPath = "E:/ansys_converter/Test_cases/solid185-tetra.cdb"
    #cdbPath = "E:/ansys_converter/Test_cases/27Model_FE.cdb"
    cdbPath = "E:/ansys_converter/CDB_docs/Pile-Cap.cdb"
    main(cdbPath)
    #runMain()