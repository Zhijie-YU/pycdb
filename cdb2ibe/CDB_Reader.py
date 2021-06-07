from collections import defaultdict
import os
import numpy as np
import warnings

from cdb2ibe.cards.utils import CDB_Keys, CDB_Keys_Exclusive, CDB_Keys_Parsable
from cdb2ibe.cards.nodes import GRID
from cdb2ibe.cards.elements import ELEMENT, ETYPE
from cdb2ibe.cards.sets import SET, RCSET
from cdb2ibe.cards.materials import MAT
from cdb2ibe.cards.constraints import D, SPC
from cdb2ibe.cards.loads import SFE
from cdb2ibe.cards.properties import SECTION


class cdbReader():
    def __init__(self):
        self._type_to_id_map = defaultdict(list)
        self.nodes = {}
        self.elements = {}
        self.sets = {}
        self.rcsets = {} # real constant set
        self.materials = {}
        self.etypes = {}
        self.spcs = {} # the final used one
        self.sspcs = {} # spc for each node (unused for writer)
        self.loads = {}
        self.properties = {} # section properties
        self.coords = {}        
        
        self._card_parser = {           
            'GRID' : (GRID, self._add_node_object),
            'ELEMENT': (ELEMENT, self._add_element_object),
            'SET': (SET, self._add_set_object),
            'RCSET': (RCSET, self._add_rcset_object),
            
            "ET": (ETYPE, self._add_etype_object),
            "SFE": (SFE, self._add_load_object),
            "SECTYPE": (SECTION, self._add_property_object) 
        }
        
        self._card_parser_add = {
            "MPTEMP": (MAT, self._add_material_object, self.materials),
            "D": (D, self._add_constraint_spc_object, self.sspcs),
        }
        
    def _add_node_object(self, node):
        key = node.nid
        assert key > 0, 'nid=%s node=%s' % (key, node)
        self.nodes[key] = node
        #self._type_to_id_map[node.type].append(key)
        
    def _add_element_object(self, elem):
        key = elem.eid
        etype = self.etypes[elem.etid].etype
        # separate orientation node
        if etype == "Beam2":
            if elem.nnode == 3:
                elem.onid = elem.nids[-1]
                elem.nids = elem.nids[:-1]
            assert len(elem.nids) == 2, key
        elif etype == "Beam3":
            if elem.nnode == 4:
                elem.onid = elem.nids[-1]
                elem.nids = elem.nids[:-1]
            assert len(elem.nids) == 3, key
        # TODO:change the ibemesh & ibeset parts
        self.elements[key] = elem
        self._type_to_id_map[etype].append(key)
        
    def _add_set_object(self, setCM):
        key = setCM.sid
        self.sets[key] = setCM
        
    def _add_rcset_object(self, rcset):
        key = rcset.rcsid
        self.rcsets[key] = rcset
        
    def _add_material_object(self, material):
        key = material.mid
        self.materials[key] = material

    def _add_etype_object(self, etype):
        key = etype.etid
        self.etypes[key] = etype
        
    def _add_constraint_spc_object(self, constraint):
        key = constraint.conid
        self.sspcs[key] = constraint        
        
    def _add_load_object(self, load):
        key = len(self.loads)+1
        self.loads[key] = load
        
    def _add_property_object(self, prop):
        key = prop.secid
        self.properties[key] = prop
        
    def linesDivision(self, lines):
        # divide lines into blocks
        nBlock = []
        eBlock = []
        cmBlock = []
        rlBlock = []
        restBlocks = []
        
        flag = 0
        for line in lines:
            cKey = line.split(',')[0].upper().strip()
            line = line.rstrip()
            
            # remove annotation and blank lines
            if line == "":
                continue
            if cKey[0] == "!":
                continue
            
            if cKey == "NBLOCK":
                flag = 1
            elif cKey == "EBLOCK":
                flag = 2
            elif cKey == "CMBLOCK":
                flag = 3
            elif cKey == "RLBLOCK":
                flag = 4
            elif cKey in CDB_Keys:
                if cKey == "ANTYPE":
                    # analysis type
                    restBlocks.append(line)
                else:
                    flag = -1
            elif cKey == "FINISH":
                break                

            if flag == 1:
                nBlock.append(line)
            elif flag == 2:
                eBlock.append(line)
            elif flag == 3:
                cmBlock.append(line)
            elif flag == 4:
                rlBlock.append(line)
            elif flag == -1:
                restBlocks.append(line)
        
        return nBlock, eBlock, cmBlock, rlBlock, restBlocks
    
    def splitLine(self, line):
        # "!" is annotation
        if '!' in line:
            line = line[:line.find('!')]
        line = line.split(',')
        line = [s.upper().strip() for s in line]
        return line
    
    def splitLineFt(self, ft, line):
        # split line according to format
        fields = []
        for ff in ft:
            tp = ff[0]
            num = ff[1]
            length = ff[2]
            for i in range(num):
                value = line[i*length:(i+1)*length].strip()
                if value == '':
                    value = '0'
                # !!! eval is very time-consuming, avoid using it !!!
                # fields.append(eval(tp)(value))
                if tp == "int":
                    fields.append(int(value))
                elif tp == "float":
                    fields.append(float(value))
            line = line[num*length:]
        return fields
    
    def splitCard(self, card):
        # split card(possibly with several lines) to list of strs
        fields = []
        for line in card:
            if ',' in line:
                line = line.rstrip(',').split(',')
            else:
                line = line.split()
            fields += [s.strip() for s in line]
        return fields
    
    def parseLFormat(self, item):
        # (3i9) => ('int', 3, 9)
        item = item.split('.')[0]
        if 'i' in item:
            id = item.index('i')
            return ('int', int(item[:id]), int(item[id+1:]))
        elif 'e' in item:
            id = item.index('e')
            return ('float', int(item[:id]), int(item[id+1:]))
        elif 'g' in item:
            id = item.index('g')
            return ('float', int(item[:id]), int(item[id+1:]))
        else:
            raise Exception("Format {} unrecognized!".format(item))
    
    def parseFormat(self, line):
        # parse format for format info
        # (3i9, 6e21.13e3) => [("int", 3, 9), ("float", 6, 21)]
        ft = []
        line = line[1:-1].split(',')
        for item in line:
            ft.append(self.parseLFormat(item))
        return ft            
    
    def parseCard(self, label, fields):
        card_class, add_card_function = self._card_parser[label]
        class_instance = card_class.add_card(fields)
        add_card_function(class_instance)
    
    def parseNB(self, nBlock):
        # parse nBlock to get node info
        line1 = self.splitLine(nBlock[0])
        assert line1[2] == "SOLID", line1
        try:
            print("Number of nodes: " + line1[4])
        except:
            pass
        
        # get format
        ft = self.parseFormat(nBlock[1])
        
        n = 0
        label = 'GRID'
        for line in nBlock[2:]:
            fields = self.splitLineFt(ft, line)
            self.parseCard(label, fields)
            n += 1
        #assert n == int(line1[4]), n
    
    def parseEB(self, eBlock):
        # parse eBlock to get element info
        line1 = self.splitLine(eBlock[0])
        assert line1[2] == "SOLID", line1
        try:
            print("Number of elements: " + line1[4])
        except:
            pass
        
        # get format
        ft = self.parseFormat(eBlock[1])
        
        n = 0
        label = 'ELEMENT'
        nl = 0
        fields = []
        for line in eBlock[2:]:
            if nl == 0:
                if fields != []:
                    self.parseCard(label, fields)
                    n += 1
                fields = self.splitLineFt(ft, line)
                nn = fields[8] # number of nodes for this element
                nf = ft[0][1] # number of fields for each line
                nl = int(np.ceil((nn-8) / nf))
                if fields[0] == -1:
                    break
            else:
                fields += self.splitLineFt(ft, line)
                nl -= 1
        #assert n == int(line1[4]), n
                
    def parseSingleCMB(self, cmBlock, sid):
        # parse a single cmBlock
        line1 = self.splitLine(cmBlock[0])
        fields = [line1[1], line1[2], int(line1[3]), sid] # name, type, num, setid
        # get format
        ft = self.parseFormat(cmBlock[1])
        
        label = 'SET'
        for line in cmBlock[2:]:
            fields += self.splitLineFt(ft, line)
        self.parseCard(label, fields)
        
    def parseCMB(self, cmBlock):
        # parse cmBlock to get set info
        # may contain several blocks
        if cmBlock == []:
            return
        idList = []
        for i,line in enumerate(cmBlock):
            cKey = line.split(',')[0].upper().strip()            
            if cKey == "CMBLOCK":
                idList.append(i)
        idList.append(len(cmBlock))
        for i in range(len(idList)-1):
            self.parseSingleCMB(cmBlock[idList[i]:idList[i+1]], i+1)
    
    def parseRLB(self, rlBlock):
        # parse rlBlock to get real constant set info (what is the use???)
        if rlBlock == []:
            return
        line1 = self.splitLine(rlBlock[0])
        num = int(line1[1])
        maxNum = int(line1[3]) # maximum number of real in one set
        print("Number of real constant sets: " + str(num))
        
        # get format
        ft1 = self.parseFormat(rlBlock[1])
        ft2 = self.parseFormat(rlBlock[2])
        
        n = 0
        label = 'RCSET'
        nl = 0
        fields = []
        for line in rlBlock[3:]:
            if nl == 0:
                if fields != []:
                    self.parseCard(label, fields)
                    n += 1
                fields = self.splitLineFt(ft1, line)
                nn = fields[1] # number of real for this set
                assert nn <= maxNum, nn
                nf = ft2[0][1] # number of reals for each line from 2nd
                nl = int(np.ceil((nn-6) / nf))
            else:
                fields += self.splitLineFt(ft2, line)
                nl -= 1
        self.parseCard(label, fields)
        n += 1
        assert n == num, n
        
    def checkSpecial(self, cKey, line):
        # deal with those disgusting formats
        # eg. several MPTEMP lines without material id
        if cKey == "MPTEMP":
            stloc = int(line.split(',')[3])
            if stloc > 1:
                return True
        return False               
        
    def getCdbCards(self, restBlocks):
        # extract parsable data from restBlocks
        cards_dict = defaultdict(list)
        lines = []
        old_cKey = None
        for line in restBlocks:
            cKey = line.split(',')[0].upper().strip()
            if cKey in CDB_Keys:
                if self.checkSpecial(cKey, line):
                    lines.append(line)
                    continue
                if old_cKey in CDB_Keys_Parsable:
                    cards_dict[old_cKey].append(lines)
                old_cKey = cKey
                lines = [line]
            else:
                if not cKey.isalpha() or cKey in CDB_Keys_Exclusive:
                    lines.append(line)
                else:                      
                    warnings.warn("Key {} not included!".format(cKey))
        if lines and old_cKey in CDB_Keys_Parsable:
            cards_dict[old_cKey].append(lines)
        return cards_dict
    
    def parseCardAdd(self, label, fields):
        # create a new class instance or add prop to an existing one
        card_class, add_card_function, data = self._card_parser_add[label]
        id = card_class.getID(fields)
        if id in data:
            data[id].add_prop(fields)
        else:
            class_instance = card_class.add_card(fields)
            add_card_function(class_instance)
    
    def parseRestCards(self, cards_dict):
        # parse each rest card
        for cKey, cards in cards_dict.items():
            for card in cards:
                fields = self.splitCard(card)
                #print(cKey, fields)
                
                if cKey in self._card_parser:
                    self.parseCard(cKey, fields)
                elif cKey in self._card_parser_add:
                    # 2 categories: directly create a card; add to a current card
                    self.parseCardAdd(cKey, fields)
                else:
                    warnings.warn("cKey {} not parsed yet!".format(cKey))                              
    
    def parseRB(self, restBlocks):
        # parse restBlocks to get other preprocessing info
        cards_dict = self.getCdbCards(restBlocks)
        self.parseRestCards(cards_dict)
        #for i,v in self.properties.items():
        #    print(i)
        #    print(v.sectype, v.props)

    def readCDB(self, cdbPath):        
        with open(cdbPath, 'r') as f:
            lines = f.readlines()
        nBlock, eBlock, cmBlock, rlBlock, restBlocks = self.linesDivision(lines)
        print("========== Reading cdb file...")
        self.parseNB(nBlock)
        self.parseCMB(cmBlock)
        self.parseRLB(rlBlock)    
        self.parseRB(restBlocks)
        # put parseEB in the end to get their etypes
        self.parseEB(eBlock)
        
        # deal with some special cases
        self.combineConstraint()

        print("========== Cdb reading complete.")
        
    def combineConstraint(self):
        # combine constraints of the same type        
        for _, con in self.sspcs.items():
            nid = con.nid
            props = con.props

            flag = 1
            for i in self.spcs:
                if props == self.spcs[i].props:
                    self.spcs[i].nids.append(nid)
                    flag = 0
                    continue
            if flag:
                conid = len(self.spcs) + 1
                self.spcs[conid] = SPC(conid, nids=[nid], props=props)
        
        