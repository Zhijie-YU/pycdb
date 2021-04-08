import numpy as np

# all cdb keys
CDB_Keys = {"NBLOCK", "EBLOCK", "CMBLOCK", "RLBLOCK", "ET", "N", "MPTEMP", "EN", "SFE", "ERESX",
            "D", "SECTYPE", "LOCAL", "CSCIR", "TYPE", "EXTOPT", "TREF",
            "IRLF", "BFUNIF", "ACEL", "OMEGA", "DOMEGA", "CGLOC",
            "CGOMEGA", "DCGOMG", "KUSE", "TIME", "ALPHAD", "BETAD",
            "DMPRAT", "DMPSTR", "CRPLIM", "NCNV", "NEQIT", "BFCUM",
            "/GO", "NSUBST", "MAT", "REAL", "CSYS", "ANTYPE"}
# excluded keys (deal with blocks which has no reference id for each line)
CDB_Keys_Exclusive = {"MPDATA", "KEYOP", "KEYOPT", "SECDATA", "SECOFFSET", "SECCONTROL",
                      "SECBLOCK"}

# currently parsable cdb keys
# TODO: "SFE","D","LOCAL","CSCIR","SEC..."
CDB_Keys_Parsable = {"MPTEMP", "ET", "D", "SFE", "SECTYPE",}

def transfer(s):
    # transfer a string to "string"/"float"/"int"
    if s.isdigit():
        s = int(s)
    else:
        if "." in s:
            s = float(s)
    return s