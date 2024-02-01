from os import listdir, pardir
import os
from PIL import Image
import numpy as np
from OpenGL.GL import *
from OpenGL.GLU import *
import pygame as pg

def loadImages(path) -> Image:
    # return array of images
    
    imagesList = listdir(path)
    # print(imagesList)
    loadedImages = []
    for image in imagesList:
        img = Image.open(path + image)
        loadedImages.append(img)

    return loadedImages

def loadImage(path):
    # return array of images
    loadedImage = Image.open(path)
    size = loadedImage.size
    loadedImage = loadedImage.transpose(Image.FLIP_TOP_BOTTOM)
    loadedImage = loadedImage.tobytes("raw", "RGBA")
    
    values = (loadedImage, size)

    return values

def createTexture(partPath=""):
    dir_path = os.path.dirname(os.path.realpath(__file__))
    if partPath[0] == "\\":
        path = dir_path + partPath
        
    else:
        path = partPath
    # your images in an array
    loaded = loadImage(path)
    image = loaded[0] 
    imageWidth, imageHeight = loaded[1]
    
    ID = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, ID)
    
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, imageWidth, imageHeight, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
    
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_REPEAT)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    
    # This is required for some reason
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    
    glGenerateMipmap(GL_TEXTURE_2D)
    
    return ID


    # Text renderer
def genTextureForText(text):
    font = pg.font.Font(None, 64)
    textSurface = font.render(text, True, (255,255,255,255), (0,0,0,100))
    ix, iy = textSurface.get_width(), textSurface.get_height()
    image = pg.image.tostring(textSurface, "RGBX", True)
    glPixelStorei(GL_UNPACK_ALIGNMENT,1)
    i = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, i)
    glTexImage2D(GL_TEXTURE_2D, 0, 3, ix, iy, 0, GL_RGBA, GL_UNSIGNED_BYTE, image)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
    glTexParameterf(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
    glTexEnvf(GL_TEXTURE_ENV, GL_TEXTURE_ENV_MODE, GL_DECAL)
    return i



if __name__ == "__main__":
    dir_path = os.path.dirname(os.path.realpath(__file__))
    # print(dir_path)
    path = dir_path + "\Images\\"

    # your images in an array
    imgs = loadImages(path)

    for img in imgs:
        img.show()