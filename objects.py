from OpenGL.GL import *
# from OpenGL.GLU import *
import numpy as np
import pyrr
import pygame as pg
from TextureHandler import createTexture
import math
from typing import List

class Object:
    def __init__(self, position, rotation, color):
        """
        Args:
            position (x, y, z): Position of the object in world space
            rotation (x, y, z)): rotation of the object in degrees
        """        
        self.name = ""
        self.position = position
        self.startPos = position
        self.rotation = rotation
        self.scale = (1, 1, 1)
        self.color = color
        self.vaoList = []
        self.vboList = []
        self.scaleX = 0
        self.scaleY = 0
        self.scaleZ = 0
        self.vertices = []
        self.newVerts = []
        self.faces = []
        self.normals = []
        # Dictionary with name and ID
        self.materials = {}
        self.textCoords = []
        self.hasText = False
        # Dictionary with name and array of faces
        self.matSwitches = {}
        self.shader = -1
        self.lightPos = [0, 5, 0]
        
    def setup(self, texture: bool):
        """Sets up an object

        Args:
            texture (bool): A boolean representing whether the object has a texture or not
        """  
        if len(self.matSwitches) > 0:      
            for material in self.matSwitches:
                vertices = self.getVertices(self.matSwitches[material])
                
                if not(texture):
                    vertex_count = len(vertices)//6
                    vertices = np.array(vertices, dtype=np.float32)

                    vao = glGenVertexArrays(1)
                    glBindVertexArray(vao)
                    vbo = glGenBuffers(1)
                    glBindBuffer(GL_ARRAY_BUFFER, vbo)
                    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)

                    # Position
                    glEnableVertexAttribArray(0)
                    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))

                    # Color
                    glEnableVertexAttribArray(1)
                    glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))
                    self.vaoList.append(vao)
                    self.vboList.append(vbo)
                    
                else:
                    self.vertex_count = len(vertices)//11
                    vertices = np.array(vertices, dtype=np.float32)

                    vao = glGenVertexArrays(1)
                    glBindVertexArray(vao)
                    vbo = glGenBuffers(1)
                    glBindBuffer(GL_ARRAY_BUFFER, vbo)
                    glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)

                    # Position
                    glEnableVertexAttribArray(0)
                    glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 44, ctypes.c_void_p(0))

                    # Color
                    glEnableVertexAttribArray(1)
                    glVertexAttribPointer(1, 2, GL_FLOAT, GL_FALSE, 44, ctypes.c_void_p(12))
                    
                    # Lighting
                    glEnableVertexAttribArray(2)
                    glVertexAttribPointer(2, 3, GL_FLOAT, GL_FALSE, 44, ctypes.c_void_p(20))
                    
                    # World position
                    glEnableVertexAttribArray(3)
                    glVertexAttribPointer(3, 3, GL_FLOAT, GL_FALSE, 44, ctypes.c_void_p(32))
                    
                    self.vaoList.append(vao)
                    self.vboList.append(vbo)
                    
        # Not loaded from an obj file   
        else:
            vertices = self.vertices
            self.vertex_count = len(vertices)//6
            vertices = np.array(vertices, dtype=np.float32)
            
            vao = glGenVertexArrays(1)
            glBindVertexArray(vao)
            vbo = glGenBuffers(1)
            glBindBuffer(GL_ARRAY_BUFFER, vbo)
            glBufferData(GL_ARRAY_BUFFER, vertices.nbytes, vertices, GL_DYNAMIC_DRAW)
            # Position
            glEnableVertexAttribArray(0)
            glVertexAttribPointer(0, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(0))
            # Color
            glEnableVertexAttribArray(1)
            glVertexAttribPointer(1, 3, GL_FLOAT, GL_FALSE, 24, ctypes.c_void_p(12))

            
            self.vaoList.append(vao)
            self.vboList.append(vbo)
            
          
        
    def move(self):
        pass
    
    def setPos(self, position):
        self.position[0] = position[0]
        self.position[1] = position[1]
        self.position[2] = position[2]
        self.startPos = position
        
    def setRotation(self, rotation):
        self.rotation[0] = rotation[0]
        self.rotation[1] = rotation[1]
        self.rotation[2] = rotation[2]        
        
    def get_model_transform(self) -> np.ndarray:
        """
            Returns the entity's model to world
            transformation matrix.
        """

        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        
        rotatedModel = pyrr.matrix44.multiply(
            m1=pyrr.matrix44.create_from_axis_rotation(
                axis = [0, 1, 0],
                theta = np.radians(self.rotation[1]), 
                dtype = np.float32
            ),
            m2=model_transform,
        )
        rotatedModel = pyrr.matrix44.multiply(
            m1=pyrr.matrix44.create_from_axis_rotation(
                axis = [0, 0, 1],
                theta = np.radians(self.rotation[2]), 
                dtype = np.float32
            ),
            m2=rotatedModel,
        )
        
        model_scale = pyrr.matrix44.create_from_scale(
            scale=self.scale
        )

        scaled_model = pyrr.matrix44.multiply(
            m1 = rotatedModel,
            m2 = model_scale
        )
        
        translatedModel = pyrr.matrix44.multiply(
            m1=scaled_model, 
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(self.position),dtype=np.float32
        )
        )
        return translatedModel
        
        
        
    def getDistance(self, point1, point2):
        xDist = math.pow(point1[0] - point2[0], 2)
        yDist =  math.pow(point1[1] - point2[1], 2)
        zDist = math.pow(point1[2] - point2[2], 2)
        return math.sqrt(xDist + yDist + zDist)
        
    def draw(self, currPos) -> None:
        """
            Draw the object.
        """            
        if len(self.matSwitches) > 0:
            for i, material in enumerate(self.matSwitches):
                if self.hasText:
                    self.useTex(self.materials[material])
                    
                if self.shader != -1:
                    glUseProgram(self.shader)
                    
                glBindVertexArray(self.vaoList[i])
                vertexCount = (len(self.matSwitches[material])) * 3
                glDrawArrays(GL_TRIANGLES, 0, vertexCount)
        else:
            if self.shader != -1:
                    glUseProgram(self.shader)
                    
            glBindVertexArray(self.vaoList[0])
            vertexCount = len(self.vertices) // 6
            glDrawArrays(GL_TRIANGLES, 0, vertexCount)
        
    def destroy(self) -> None:
        """
            Free any allocated memory.
        """
        for vao in self.vaoList:
            glDeleteVertexArrays(1,(vao,))
            
        for vbo in self.vboList:
            glDeleteBuffers(1,(vbo,))
        
    def update(self, position, rotation=()) -> None:
        self.position[0] += position[0]
        self.position[1] += position[1]
        self.position[2] += position[2]
        
        if rotation != ():
            self.rotation = rotation

        # self.rotation[1] += 0.25
        
        # if self.rotation[1] > 360:
        #     self.rotation[1] -= 360
        
    def getVertices(self, faces):
        """
        Returns an array of vertices from the given face

        Args:
            faces (list of tuples): A list of tuples of length 3, where each index is a list of 3 values,
            faces[0][0][0] = index of vertice,
            faces[0][0][1] = texture coordinate index,
            faces[0][0][2] = normal index

        Returns:
            list[int]: A list of vertices from the given face
        """        
        
        vertices = []
        for i, face in enumerate(faces):
                for triangle in face:
                    vertnum = int(triangle[0]) - 1
                    shapeVerts = self.vertices[vertnum]
                    normalNum = int(triangle[2]) - 1
                        
                    x = float(shapeVerts[0])
                    y = float(shapeVerts[1])
                    z = float(shapeVerts[2])

                    
                    if self.color is None:
                        texnum = int(triangle[1]) - 1
                        s = self.textCoords[texnum][0]
                        t = self.textCoords[texnum][1]
                        
                        nx = self.normals[normalNum][0]
                        ny = self.normals[normalNum][1]
                        nz = self.normals[normalNum][2]
                        
                        # Vertice coordinates
                        vertices.append(x)
                        vertices.append(y)
                        vertices.append(z)
                        
                        # Texture coordinates
                        vertices.append(s)
                        vertices.append(t)
                        
                        # Vertice normals
                        vertices.append(nx)
                        vertices.append(ny)
                        vertices.append(nz)
                        
                        # Object position
                        vertices.append(self.position[0])
                        vertices.append(self.position[1])
                        vertices.append(self.position[2])
                        
                        continue
                    
                    r = float(self.color[0])
                    g = float(self.color[1])
                    b = float(self.color[2])
                    
                    vertices.append(x)
                    vertices.append(y)
                    vertices.append(z)
                    vertices.append(r)
                    vertices.append(g)
                    vertices.append(b)

        return vertices
            
    def useTex(self, texture) -> None:
        """
            Arm the texture for drawing.
        """

        glActiveTexture(GL_TEXTURE0)
        glBindTexture(GL_TEXTURE_2D, texture)
    
    def setFaces(self, faces):
        self.faces = faces
    
    def setNormals(self, normals):
        self.normals = normals
    
    def setTextCoords(self, textCoords):
        self.textCoords = textCoords
    
    def setMaterials(self, materials, matSwitches):
        self.hasText = len(materials) > 0
        self.materials = materials
        self.matSwitches = matSwitches
        
    def setShader(self, shader):
        self.shader = shader
        
    def setVertices(self, vertices):
        self.vertices = vertices
        
    def setScale(self, scale):
        self.scale = scale
    
    
class Ground(Object):
    vertices = [
        -1,  1, -1,  0, 1,
        -1, -1, -1,  0, 0,
         1, -1, -1,  1, 0,
         
         1, -1, -1, 1, 0,
         1,  1, -1, 1, 1,
        -1,  1, -1, 0, 1
    ]
    
    def setTexture(self, path):
        """
        Sets a texture for the ground plane

        Args:
            path (str): path to the texture
        """        
        self.texture = createTexture(path)
        self.hasText = True
    
    def update(self, position) -> None:
        self.position = position
        
        
class Light(Object):
    def __init__(self, position, color, strength: float, enabled: int, name="light"):
        """_summary_

        Args:
            position (list): position as a list in x, y, z format
            color (list): color as a list in r, g, b format
            strength (float): strength of the light
        """        
        self.position = position
        self.startPos = position
        self.color = color
        self.strength = strength
        self.name = name
        self.rotation = [0, 0, 0]
        self.scale = [1, 1, 1]
        self.enabled = enabled
        self.distance = math.sqrt(math.pow(self.position[0], 2) + math.pow(self.position[2], 2))
        
    def get_model_transform(self) -> np.ndarray:
        """
            Returns the entity's model to world
            transformation matrix.
        """

        model_transform = pyrr.matrix44.create_identity(dtype=np.float32)
        
        translatedModel = pyrr.matrix44.multiply(
            m1=model_transform, 
            m2=pyrr.matrix44.create_from_translation(
                vec=np.array(self.position),dtype=np.float32
        )
        )
        rotatedModel = pyrr.matrix44.multiply(
            m1=pyrr.matrix44.create_from_axis_rotation(
                axis = [0, 1, 0],
                theta = np.radians(self.rotation[1]), 
                dtype = np.float32
            ),
            m2=translatedModel,
        )
        
        return translatedModel
        
import math

def calculate_legs(hypotenuse, angle_degrees):
    angle_radians = math.radians(angle_degrees)
    
    # Calculate legs using sine function
    x = hypotenuse * math.sin(angle_radians)
    z = hypotenuse * math.cos(angle_radians)

    return x, z

