from inc_noesis import *

def registerNoesisTypes():
    handle = noesis.register( \
        "TOCA Touring Car Championship / Colin McRae Rally (1997/1998) models", ".c3d")
        
    noesis.setHandlerTypeCheck(handle, cmrModelCheckType)
    noesis.setHandlerLoadModel(handle, cmrModelLoadModel)
        
    return 1 
    
    
class Vector4I:
    def __init__(self, reader): 
        self.reader = reader
        self.x = 0
        self.y = 0
        self.z = 0
        self.w = 0
        
    def read(self):
        self.x, self.y, self.z, self.w = noeUnpack("iiii", self.reader.readBytes(16))
 
    def getStorage(self):
        return (self.x / 65536.0, self.y / 65536.0, self.z / 65536.0, self.w / 65536.0)
        

class Vector3I:
    def __init__(self, reader): 
        self.reader = reader
        self.x = 0
        self.y = 0
        self.z = 0
        
    def read(self):
        self.x, self.y, self.z = noeUnpack("iii", self.reader.readBytes(12))
 
    def getStorage(self):
        return (self.x / 65536.0, self.y / 65536.0, self.z / 65536.0)  
        
        
class Vector2I:
    def __init__(self, reader): 
        self.reader = reader
        self.x = 0
        self.y = 0
        
    def read(self):
        self.x, self.y = noeUnpack("ii", self.reader.readBytes(8))
 
    def getStorage(self):
        return (self.x / 65536.0, self.y / 65536.0)         
        
        
class Vector3UI16:
    def __init__(self, reader): 
        self.reader = reader
        self.x = 0
        self.y = 0
        self.z = 0
        
    def read(self):
        self.x, self.y, self.z = noeUnpack("HHH", self.reader.readBytes(6))
        
    def getStorage(self):
        return (self.x, self.y, self.z)
    
    
class Matrix4x4:
    def __init__(self, reader): 
        self.reader = reader
        self.x = Vector4F(self.reader)
        self.y = Vector4F(self.reader)
        self.z = Vector4F(self.reader)    
        self.pos = Vector4F(self.reader)  
        
    def read(self):
        self.x.read()        
        self.y.read()        
        self.z.read()        
        self.pos.read()   

    def getStorage(self):
        return (self.x.getStorage(), self.y.getStorage(), self.z.getStorage(), self.pos.getStorage())         
    
 
class CMRMatrix:
    def __init__(self, reader):
        self.reader = reader
        self.matrix = Matrix4x4()
        
    def read(self):
        self.size = self.reader.readUInt()
        self.reader.seek(4, NOESEEK_REL)
        self.matrix.read()
        self.reader.seek(8, NOESEEK_REL)
        self.reader.seek(self.size - 80, NOESEEK_REL)
        
    
class CMRVertex:
    def __init__(self, reader):
        self.reader = reader
        self.pos = Vector3I(self.reader)  
        self.normal = Vector3I(self.reader)    
        self.uv = Vector2I(self.reader)

    def read(self):
        self.pos.read()
        self.uv.read()  
        self.normal.read()        
      
        
class CMRFace:
    def __init__(self, reader): 
        self.reader = reader
        self.indexes = Vector3UI16(self.reader)
        
    def read(self):
        self.reader.seek(2, NOESEEK_REL)
        self.indexes.read()     
        self.reader.seek(16, NOESEEK_REL)
        
        
class CMRModelMesh:
    def __init__(self, reader):
        self.reader = reader
        self.name = ""
        self.vertices = []              
        self.faces = [] 
        self.matIndex = 0        
          
    def readHeader(self):
        self.name = self.reader.readBytes(12).split(b"\x00")[0].decode("ascii")
        self.size = self.reader.readUInt() 
        self.vertNum = self.reader.readUShort() 
        self.faceNum = self.reader.readUShort() 
        self.reader.seek(28, NOESEEK_REL)
        
    def readVertices(self):
        for i in range(self.vertNum):   
            vertex = CMRVertex(self.reader)
            vertex.read()
            self.vertices.append(vertex)
        
    def readFaces(self):
        for i in range(self.faceNum):  
            face = CMRFace(self.reader)
            face.read()
            self.faces.append(face)              
        
    def read(self):
        self.readHeader()      
        self.readVertices()           
        self.readFaces()     
        # self.matIndex = self.reader.readUShort()        
  
        
class CMRTexture: 
    def __init__(self, reader):
        self.reader = reader    
        self.name = ""
        self.data = None
        
    def read(self):   
        self.name = self.reader.readBytes(12).split(b"\x00")[0].decode("ascii") 
        size = self.reader.readUInt() 
        self.data = self.reader.read(size)
 
 
class CMRModel:
    def __init__(self, reader): 
        self.reader = reader
        self.matrixes = []
        self.meshes = []
        self.textures = []
        
    def readHeader(self):
        self.reader.seek(4, NOESEEK_ABS)
        self.version = self.reader.readUInt()
        self.size = self.reader.readUInt()        
        self.matrixNum = self.reader.readUShort() 
        self.meshNum = self.reader.readUShort()
        self.texNum = self.reader.readUInt()
        self.matrixOffset = self.reader.readUInt()
        self.meshesOffset = self.reader.readUInt()
        self.textureOffset = self.reader.readUInt() 
  
    def readTextures(self):
        self.reader.seek(self.textureOffset, NOESEEK_ABS)    
      
        for i in range(self.texNum):    
            texture = CMRTexture(self.reader)
            texture.read()           
            self.textures.append(texture)              
            
    def readMeshes(self):
        self.reader.seek(self.meshesOffset, NOESEEK_ABS)    
      
        for i in range(self.meshNum):    
            mesh = CMRModelMesh(self.reader)
            mesh.read()           
            self.meshes.append(mesh)           
       
    def read(self):
        self.readHeader()       
        self.readMeshes()     
        self.readTextures()     
        
        
def cmrModelCheckType(data):

    return 1     
    

def cmrModelLoadModel(data, mdlList):
    noesis.logPopup()
    model = CMRModel(NoeBitStream(data))
    model.read()
    
    ctx = rapi.rpgCreateContext()
    
    #transMatrix = NoeMat43( ((-1, 0, 0), (0, 1, 0), (0, 0, 1), (0, 0, 0)) ) 
    #rapi.rpgSetTransform(transMatrix)
    
    # load textures
    materials = []
    textures = [] 
        
    for index, tex in enumerate(model.textures):
        texture = rapi.loadTexByHandler(tex.data, ".bmp")
        texture.name = tex.name
        material = NoeMaterial("mat" + str(index), tex.name)
        materials.append(material)
        textures.append(texture)          
 
    for msh in model.meshes: 
        rapi.rpgSetMaterial("mat0")        
        rapi.rpgSetName(msh.name)    
        for i in range(msh.faceNum):
            face = msh.faces[i]
            rapi.immBegin(noesis.RPGEO_TRIANGLE)
            for k in range(3):              
                vIndex = face.indexes.getStorage()[k] 
                rapi.immUV2(msh.vertices[vIndex].uv.getStorage())  
                rapi.immNormal3(msh.vertices[vIndex].normal.getStorage())  
                     
                rapi.immVertex3(msh.vertices[vIndex].pos.getStorage())      
        
            rapi.immEnd() 
  
    mdl = rapi.rpgConstructModelSlim() 
    
    # set materials
    if materials:    
        mdl.setModelMaterials(NoeModelMaterials(textures, materials))    
    mdlList.append(mdl)
    
    #rapi.setPreviewOption("setAngOfs", "0 0 0")
    rapi.setPreviewOption("setAnimSpeed", "20.0")
	
    return 1        