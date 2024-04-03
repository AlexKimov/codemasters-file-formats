#
#
#


from inc_noesis import *
import os
import noewin
import noewinext
from collections import OrderedDict 


def registerNoesisTypes():
    handle = noesis.register("Toca Touring Car Championship archive", ".bfp")
    noesis.setHandlerExtractArc(handle, bmfExtractResources)
    
    return 1
  
  
class FileRecord:
    def __init__(self):   
        self.offset = 0
        self.size = 0
        self.name = ""
        
        
class BMFFile:
    def __init__(self, reader):
        self.reader = reader
        self.tableRecords = []
        self.fileCount = 0
        self.tableSize = 0
        
    def readHeader(self, reader):
        self.fileCount = reader.readUInt()
        self.tableSize = reader.readUInt()
        reader.seek(4, NOESEEK_REL)
        
    def readTable(self, reader):
        for i in range(self.fileCount):
            record = FileRecord()
            
            record.name = reader.readBytes(16).decode("ascii")
            zeroPos = record.name.find('\0')
            if zeroPos:
               record.name = record.name[0:zeroPos] 
               
            record.offset = reader.readUInt()
            record.size = reader.readUInt()
            
            self.tableRecords.append(record)
        
    def read(self):
        self.readHeader(self.reader)
        self.readTable(self.reader)
    
    
def bmfExtractResources(fileName, fileLen, justChecking):    
    with open(fileName, "rb") as f:
        if justChecking: #it's valid
            return 1   
        
        filereader = NoeBitStream(f.read())    
    
        bmf = BMFFile(filereader)
        bmf.read()
        
        for fileRec in bmf.tableRecords:  
            bmf.reader.seek(fileRec.offset + bmf.tableSize + 12, NOESEEK_ABS)
            fileData = bmf.reader.readBytes(fileRec.size)            
            rapi.exportArchiveFile(fileRec.name, fileData)
       
    return 1