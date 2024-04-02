from inc_noesis import *


def registerNoesisTypes():
    handle = noesis.register("Toca race 1998 palette textures", ".bfa")
    noesis.setHandlerLoadRGBA(handle, cmrLoadRGBA)
    noesis.setHandlerTypeCheck(handle, cmrCheckType)
    
    return 1


class CMRImage():
    def __init__(self, reader):
        self.reader = reader    
        self.palette = None
        self.data = None
        self.width = 0
        self.height =  0
        
    def read(self):
        size = self.reader.readUInt()
        self.width = self.reader.readUShort()
        self.height = self.reader.readUShort()
        self.num = self.reader.readUShort()
        self.reader.seek(6, NOESEEK_REL)
        self.palette = self.reader.readBytes(self.num*4)
        self.data = self.reader.readBytes(self.width*self.height)  


class CMRFileRec:
    def __init__(self, reader):
        self.reader = reader
        self.offset = 0
        self.name = ""
        
    def read(self):    
        self.name =  noeAsciiFromBytes(self.reader.readBytes(12))

        self.offset = self.reader.readUInt()
        self.reader.seek(8, NOESEEK_REL)
           
           
class CMRImageArchive:
    def __init__(self, reader):
        self.reader = reader
        self.num = 0
        self.fileRecs = []
       
    def readHeader(self):
        self.num = self.reader.readUShort()
        self.reader.seek(4, NOESEEK_REL)
        
    def readFileHeaders(self):
        for i in range(self.num):
            fc = CMRFileRec(self.reader)
            fc.read()
            self.fileRecs.append(fc)
            
    def getImages(self):
        for f in self.fileRecs:
            self.reader.seek(f.offset  + self.num * 12, NOESEEK_ABS)
            img = CMRImage(self.reader)
            img.read()
            img.name = f.name
            yield img
        
    def read(self):
        self.readHeader()
        self.readFileHeaders()        
  
  
def cmrCheckType(data):
    #
    return 1
    
    
def cmrLoadRGBA(data, texList):
    #noesis.logPopup()
    
    tcrImage = CMRImageArchive(NoeBitStream(data))
    tcrImage.read()
     
    for image in tcrImage.getImages():    
        imageData = rapi.imageDecodeRawPal(image.data, image.palette, image.width, \
            image.height, 8, "r8g8b8p8")   
        
        texList.append(NoeTexture(image.name, image.width, image.height, imageData, noesis.NOESISTEX_RGBA32)) 
            
        
    return 1

