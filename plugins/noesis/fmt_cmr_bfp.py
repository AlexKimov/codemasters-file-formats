from inc_noesis import *


def registerNoesisTypes():
    handle = noesis.register("Toca race 1998 pictures", ".bfp")
    noesis.setHandlerLoadRGBA(handle, BFPLoadRGBA)
    noesis.setHandlerTypeCheck(handle, BFPCheckType)

    return 1
       
     
class BFPFileRec:
    def __init__(self, reader):
        self.reader = reader
        self.offset = 0
        self.size = 0
        self.name = ""
        
    def read(self):    
        self.name = noeAsciiFromBytes(self.reader.readBytes(16))
        self.offset = self.reader.readUInt()
        self.size = self.reader.readUInt()
 
 
class BFPImageArchive:
    def __init__(self, reader):
        self.reader = reader
        self.num = 0
        self.sectionSize = 0
        self.fileRecs = []
       
    def readHeader(self):
        self.num = self.reader.readUInt()
        self.sectionSize = self.reader.readUInt()
        self.size = self.reader.readUInt()
        
    def readFileHeaders(self):
        for i in range(self.num):
            fc = BFPFileRec(self.reader)
            fc.read()
            self.fileRecs.append(fc)
  
    def getImagesData(self):
       for fc in self.fileRecs:          
           self.reader.seek(fc.offset + self.sectionSize + 12, NOESEEK_ABS)
           yield self.reader.readBytes(fc.size)
  
    def read(self):
        self.readHeader()
        self.readFileHeaders()        
  
  
def BFPCheckType(data):
    #
    return 1
    
    
def BFPLoadRGBA(data, texList):
    noesis.logPopup()
    
    tcrImage = BFPImageArchive(NoeBitStream(data))
    tcrImage.read()
     
    for imageData in tcrImage.getImagesData():
        if imageData[0:2] == b'BM': 
            texure = rapi.loadTexByHandler(imageData, ".bmp")    
            texList.append(texure)       
        
    return 1

