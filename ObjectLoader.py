from objects import Object
import os.path
from TextureHandler import createTexture

class ObjectLoader():
    def __init__(self) -> None:
        pass
    
    def load(self, path, color=None) -> Object:
        # scene = pywavefront.Wavefront(path)
        # if color is None:
        #     color = (1, 1, 1)
        newObj = Object([0, 0, 0], [1, 1, 1, 1], color)
        vertices = []
        faces = []
        normals = []
        materials = {}
        textCoords = []
        matSwitches = {}
        matName = ""
        first = True

        
        # Read content from file
        lines = ""
        with open(path, 'r') as fp:
            lines = fp.readlines()
            
        for line in lines:
            line =  line.replace("\n", "")
            split = line.split(" ")

            
            if(split[0] == "v"):
                x = float(split[1])
                y = float(split[2])
                z = float(split[3])

                vertices.append((x, y, z))
                
            elif(split[0] == "f"):
                triangle = line[2:len(line)]
                triangle = triangle.split(" ")

                vertex1 = triangle[0].split("/")
                vertex2 = triangle[1].split("/")
                vertex3 = triangle[2].split("/")
                
                faces.append((vertex1, vertex2, vertex3))

            elif(split[0] == "vn"):
                nums = line.split(" ")
                x = float(nums[1])
                y = float(nums[2])
                z = float(nums[3])
                normal = (x, y, z)
                normals.append(normal)
                
            elif(split[0] == "mtllib"):
                materials = self.loadMaterials(os.path.dirname(path), split[1])
                
            elif split[0] == "vt":
                coord = (float(split[1]), float(split[2]))
                textCoords.append(coord)
                
            elif(split[0] == "usemtl"):
                # matSwitches[lineCount] = split[1]
                if first:
                    first = False
                    matName = split[1]

                else:
                    matSwitches[matName] = faces
                    matName = split[1]

                faces = []
                
        matSwitches[matName] = faces
        
        newObj.setFaces(faces)
        newObj.setVertices(vertices)
        
        newObj.setNormals(normals)
        newObj.setTextCoords(textCoords)
        newObj.setMaterials(materials, matSwitches)

        return newObj
    
    def loadMaterials(self, path, file) -> dict:
        lines = ""
        materials = {}
        name = ""
        ID = 0
        
        with open(path + "\\" +  file, 'r') as fp:
            lines = fp.readlines()
            
        for line in lines:
            line =  line.replace("\n", "")
            split = line.split(" ")
            
            if split[0] == "newmtl":
                name = split[1]
                
                
            elif split[0] == "map_Kd":
                path = split[1]
   
                if len(split) > 2:
                    for i in range(2, len(split)):
                        path = path + " "
                        path = path + split[i]
                        
                splitPath = path.split("/")
                finalPart = splitPath[len(splitPath) - 1]
                # print(path)
                
                path = os.path.dirname(os.path.realpath(__file__)) + "\Images\\" + finalPart
                ID = createTexture(path)
                materials[name] = ID
                
        return materials