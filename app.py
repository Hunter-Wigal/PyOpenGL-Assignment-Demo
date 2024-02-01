#!/usr/bin/env python3.10

import pygame as pg
from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram, compileShader
from OpenGL.GLU import *
import pyrr
from objects import *
import os
from typing import List
from ObjectLoader import ObjectLoader
from math import sin, cos, radians
from random import randint


def clamp(value, minimum, maximum) -> float:
    """Returns a value that is within the provided bounds

    Args:
        value (float): The value to clamp tp a bounds
        minimum (float): The lower bounds
        maximum (float): The upper bounds

    Returns:
        float: A value that is within the provided bounds
    """
    if value >= maximum:
        return maximum
    elif value <= minimum:
        return minimum
    else:
        return value


def create_shader(vertex_filepath: str, fragment_filepath: str) -> int:
    """
    Compile and link shader modules to make a shader program.

    Parameters:

        vertex_filepath: path to the text file storing the vertex
                        source code

        fragment_filepath: path to the text file storing the
                            fragment source code

    Returns:

        A handle to the created shader program
    """

    with open(vertex_filepath, "r") as f:
        vertex_src = f.readlines()

    with open(fragment_filepath, "r") as f:
        fragment_src = f.readlines()

    shader = compileProgram(
        compileShader(vertex_src, GL_VERTEX_SHADER),
        compileShader(fragment_src, GL_FRAGMENT_SHADER),
    )

    return shader


class MainWindow:
    def __init__(self, width, height):
        self.display = (width, height)

        self.dir_path = os.path.dirname(os.path.realpath(__file__))

        pg.init()
        self.display = pg.display.list_modes()[10]
        self.ratio = self.display[0] / self.display[1]

        pg.display.set_mode(self.display, pg.OPENGL | pg.DOUBLEBUF, display=0)
        self.OL = ObjectLoader()

        self.moveSpeed = 0.1
        self.currPos = [0, 0, 0]
        self.rotation = [0, 0, 0]

        self.setup_opengl()
        self.createAssets()

        # self._set_onetime_uniforms(self.colorshader)

        # self._get_uniform_locations(self.colorshader)

        self._set_onetime_uniforms(self.textureshader)

        self._get_uniform_locations(self.textureshader)

        self.clock = pg.time.Clock()

    # Set OpenGl specific configurations
    def setup_opengl(self):
        glClearColor(0.1, 0.2, 0.2, 1)
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_CULL_FACE)
        glCullFace(GL_BACK)


    def createAssets(self):
        self.objects: List[Object] = []

        # self.colorshader = create_shader(self.dir_path + "/shaders/colorvertex.glsl", self.dir_path + "/shaders/colorfragment.glsl")
        self.textureshader = create_shader(
            self.dir_path + "/shaders/texvertex.glsl",
            self.dir_path + "/shaders/texfragment.glsl",
        )

        objectPaths = [
            "watertower.obj",
            "ground.obj",
            "house.obj",
            "street.obj",
            "shed.obj",
            "skyscraper.obj",
            "tree.obj",
            "budgetskyscraper.obj",
            "budgetskyscraper2.obj",
            "budgetskyscraper3.obj",
            "house2.obj",
            "skybox.obj",
            "door.obj",
            "tree.obj",
            "person.obj",
            "hand.obj",
        ]
        objectPositions = [
            (15, -1, -20),
            (0, -1.05, 0),
            (0, -1, -20),
            (0, -1, -5),
            (0, -1, -33),
            (5, 0, 15),
            (4, -1, -11),
            (21, -1, 7),
            (31, -1, 7),
            (41, -1, 7),
            (-25, -1, -20),
            (0, 0, 0),
            (-0.58, -0.95, -14.8),
            (-4, -1, -11),
            (2, 0.2, -9),
            (2, 0.2, -9),
        ]
        objectScales = [
            (0.5, 0.5, 0.5),
            (50, 1, 50),
            (0.6, 0.6, 1),
            (30, 1, 1),
            (0.4, 0.4, 0.4),
            (3, 1.5, 3),
            (1, 1, 1),
            (1, 1, 1),
            (1, 1, 1),
            (1, 1, 1),
            (1, 0.6, 1),
            (3, 3, 3),
            (0.6, 0.6, 1),
            (1, 1, 1),
            (0.6, 0.6, 0.6),
            (0.6, 0.6, 0.6),
        ]
        objectRotations = [
            (0, 0, 0),
            (0, 0, 0),
            (0, 180, 0),
            (0, 90, 0),
            (0, -90, 0),
            (0, 90, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 180, 0),
            (0, 0, 0),
            (180, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
            (0, 0, 0),
        ]

        for i, object in enumerate(objectPaths):
            if i > len(objectPositions) - 1:
                i = 0
            name = object
            object = self.OL.load(self.dir_path + "\\Objects\\" + object)
            object.name = name
            object.setShader(self.textureshader)
            object.setup(True)
            object.setPos(objectPositions[i])
            object.setScale(objectScales[i])
            object.setRotation(objectRotations[i])
            self.objects.append(object)

        pos = [41, -1, 7]
        self.generate_buildings(5, pos, 10, (1, 1, 1))
        pos = [15, -1, -20]
        self.generate_buildings(5, pos, -10, (1, 180, 1))

    def generate_buildings(self, num, pos, possibleOffset, rotation):
        skyscrapers = [
            "budgetskyscraper.obj",
            "budgetskyscraper2.obj",
            "budgetskyscraper3.obj",
        ]
        houses = ["house.obj", "house2.obj", "house3.obj"]
        buildings = [skyscrapers, houses]
        offsets = [20, 35]

        for i in range(num):
            building = randint(0, 1)
            buildingNum = randint(0, 2)
            pickedPath = buildings[building][buildingNum]
            zOffset = 0
            # House
            if building and buildingNum == 0:
                zOffset = possibleOffset

            xOffset = pos[0] + offsets[building] / 2
            pos[0] += offsets[building]

            object = pickedPath
            object = self.OL.load(self.dir_path + "\\Objects\\" + object)
            object.name = pickedPath + str(i)
            object.setShader(self.textureshader)
            object.setup(True)
            object.setPos((xOffset, pos[1], pos[2] + zOffset))
            object.setScale((1, 1, 1))
            object.setRotation(rotation)
            self.objects.append(object)

    def _set_onetime_uniforms(self, shader) -> None:
        """
        Set projection matrix in shader
        """
        glUseProgram(shader)

        projection_transform = pyrr.matrix44.create_perspective_projection(
            fovy=45, aspect=self.ratio, near=0.1, far=100, dtype=np.float32
        )
        
        glUniformMatrix4fv(
            glGetUniformLocation(shader, "projection"),
            1,
            GL_FALSE,
            projection_transform,
        )

    def _get_uniform_locations(self, shader) -> None:
        """
        Query and store the locations of shader uniforms
        """

        glUseProgram(shader)
        self.modelMatrixLocation = glGetUniformLocation(shader, "model")
        
        # Used for adding unfinished lighting functionality, only provides single spotlight
        self.lightStructLocation = [
            glGetUniformLocation(shader, "Sun.position"),
            glGetUniformLocation(shader, "Sun.color"),
            glGetUniformLocation(shader, "Sun.strength"),
        ]
        self.listArrayLocation = glGetUniformLocation(shader, "Lights")
        self.lightListLocation = {}
        for i in range(10):
            self.lightListLocation[
                "Light" + str(i) + " position"
            ] = glGetUniformLocation(shader, f"Lights[{i}].position")
            self.lightListLocation["Light" + str(i) + " color"] = glGetUniformLocation(
                shader, f"Lights[{i}].color"
            )
            self.lightListLocation[
                "Light" + str(i) + " strength"
            ] = glGetUniformLocation(shader, f"Lights[{i}].strength")
            self.lightListLocation[
                "Light" + str(i) + " enabled"
            ] = glGetUniformLocation(shader, f"Lights[{i}].enabled")
        # self.viewLocation = glGetUniformLocation(shader, "view")

    def run(self):
        running = 1
        self.xRot = 0
        self.yRot = 0

        escaped = False
        
        # Used in opening the door
        opening = False
        closing = False
        opened = False
        closed = True
        rotationY = 0

        canSwitch = True
        screenTimer = 0

        # Used in changing the time of day, affects lighting
        setting = False
        night = False
        rising = False
        day = True

        # Unfinished feature
        self.lightList: List[Light] = []
        self.light1 = Light([0, 0, 0], [1, 1, 1], 1, -1)
        self.light2 = Light([0, 0, 30], [1, 1, 1], 1, -1)

        self.lightList.append(self.light1)
        self.lightList.append(self.light2)

        # Used in animating the character waving
        waving = False
        currWaving = False
        times = 0
        up = False
        down = False
        amount = 0

        # Set mouse to center
        pg.mouse.set_pos(self.display[0] / 2, self.display[1] / 2)
        pg.mouse.set_visible(False)
        while running:
            self.moveSpeed = 0.15
            self.xUpdate = 0
            self.yUpdate = 0
            self.zUpdate = 0
            screenChanged = False

            # check events
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    self.quit()

            # Get pressed keys
            pressed = pg.key.get_pressed()

            centerPos = self.display[0] / 2, self.display[1] / 2

            # Determine world rotation based on mouse position
            dx, dy = pg.mouse.get_rel()
            self.yRot += dx * 0.25
            self.xRot = clamp(self.xRot + dy * 0.25, -85.0, 90.0)
            self.rotation[0] = self.xRot
            self.rotation[1] = self.yRot

            # Handle escaping the applcation
            if pressed[pg.K_ESCAPE]:
                escaped = True
                pg.mouse.set_visible(True)

            elif pg.mouse.get_pressed()[0]:
                if escaped:
                    pg.mouse.set_visible(False)
                    escaped = False

            # Slow down the rate of fullscreening
            if pressed[pg.K_f]:
                if canSwitch:
                    pg.display.toggle_fullscreen()
                    screenChanged = True
                    canSwitch = False

            # Move the mouse to the middle if it leaves the screen
            mousePos = pg.mouse.get_pos()
            if escaped == False:
                if mousePos[0] > self.display[0] - 100:
                    pg.mouse.set_pos(centerPos)

                elif mousePos[1] > self.display[1] - 100:
                    pg.mouse.set_pos(centerPos)

                elif mousePos[0] < 100:
                    pg.mouse.set_pos(centerPos)

                elif pg.mouse.get_pos()[1] < 100:
                    pg.mouse.set_pos(centerPos)

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            self.fps = self.clock.get_fps()
            pg.display.set_caption("FPS: %0.2d" % self.fps)

            # Sprint while pressed
            if pressed[pg.K_q]:
                self.moveSpeed = 0.5

            # Movement keys
            if pressed[pg.K_a]:
                self.moveLeft(self.yRot)

            if pressed[pg.K_d]:
                self.moveRight(self.yRot)

            if pressed[pg.K_w]:
                self.moveForward(self.yRot)

            if pressed[pg.K_s]:
                self.moveBackward(self.yRot)

            # "Flying" keys
            if pressed[pg.K_SPACE]:
                self.currPos[1] += 0.1
                self.yUpdate -= 0.1
            if pressed[pg.K_LSHIFT]:
                self.currPos[1] -= 0.1
                self.yUpdate += 0.1

            # Change time of day
            if pressed[pg.K_n]:
                if not (night):
                    setting = True
                    for light in self.lightList:
                        light.enabled = 1
                else:
                    rising = True
                    for light in self.lightList:
                        light.enabled = 0

            if setting and self.light.strength > 0.15:
                self.light.strength -= 0.1 / self.fps
            elif rising and self.light.strength < 1:
                self.light.strength += 0.1 / self.fps

            if self.light.strength <= 0.15:
                setting = False
                night = True
                self.light.strength = 0.15

            elif self.light.strength >= 1:
                rising = False
                day = True
                night = False
                self.light.strength = 1

            # Start the character animation
            if pressed[pg.K_e]:
                if not (waving):
                    waving = True
                    up = True
                    print("waving")

            glUniform3fv(self.lightStructLocation[0], 1, self.light.position)
            glUniform3fv(self.lightStructLocation[1], 1, self.light.color)
            glUniform1f(self.lightStructLocation[2], self.light.strength)

            # Doesn't work as intended
            for i, light in enumerate(self.lightList):
                light.update((self.xUpdate, self.yUpdate, self.zUpdate))

                light.position = self.getGlobalRotation(light.get_model_transform())[
                    :3, 3
                ]

                position = self.lightListLocation["Light" + str(i) + " position"]
                color = self.lightListLocation["Light" + str(i) + " color"]
                strength = self.lightListLocation["Light" + str(i) + " strength"]
                enabled = self.lightListLocation["Light" + str(i) + " enabled"]

                glUniform3fv(position, 1, light.position)
                glUniform3fv(color, 1, light.color)
                glUniform1f(strength, light.strength)
                glUniform1f(enabled, light.enabled)

            # Draw all of the objects
            for object in self.objects:
                # Move the skybox with the player
                if object.name != "skybox.obj":
                    object.update((self.xUpdate, self.yUpdate, self.zUpdate))

                # Skip objects at a certain distance, except the ground and street
                if (
                    object.name != "ground.obj"
                    and object.name != "street.obj"
                    and object.name != "skybox.obj"
                ):
                    distance = object.getDistance(object.startPos, self.currPos)
                    if distance > 65:
                        continue

                # Open or close a door on a button press
                if object.name == "door.obj":
                    if object.getDistance((0, 0, 0), object.position) < 5:
                        if not (opening) and not (closing):
                            if pressed[pg.K_o]:
                                if closed:
                                    opening = True

                                elif opened:
                                    closing = True
                    if opening:
                        rotationY += 1

                    elif closing:
                        rotationY -= 1

                    object.setRotation([0, rotationY, 0])

                if object.name == "hand.obj":
                    if waving:
                        if amount >= 90:
                            down = True
                            up = False
                            amount = 90
                            times += 1

                        elif amount <= 0:
                            up = True
                            down = False
                            times += 1
                        if up:
                            amount += 1.5
                        elif down:
                            amount -= 1.5

                        object.setRotation([0, 0, amount])
                    if times > 4:
                        waving = False
                        up = False
                        down = False
                        times = 0
                        amount = 0

                globalRot = self.getGlobalRotation(object.get_model_transform())

                glUniformMatrix4fv(self.modelMatrixLocation, 1, GL_FALSE, globalRot)

                # glUniformMatrix4fv(self.viewLocation, 1, GL_FALSE, self.get_view_transform())
                # self.light.update((self.yUpdate, -self.xUpdate, self.zUpdate))

                if object.name.lower().find("light") == -1:
                    object.draw(self.currPos)

            # Outside object loop
            if rotationY >= 90:
                opened = True
                closed = False
                opening = False
                rotationY = 90
            elif rotationY <= 0:
                closing = False
                opened = False
                closed = True
                rotationY = 0

            if screenChanged or screenTimer > 0:
                screenTimer += 1
                if screenTimer >= 90:
                    canSwitch = True
                    screenTimer = 0

            pg.display.flip()

            self.clock.tick(90)

    # Used in determining certain object positions
    def getGlobalRotation(self, transform: np.ndarray):
        rotationy = pyrr.matrix44.create_from_axis_rotation(
            axis=[0, 1, 0], theta=np.radians(self.yRot), dtype=np.float32
        )

        rotationx = pyrr.matrix44.create_from_axis_rotation(
            axis=[1, 0, 0], theta=np.radians(self.xRot), dtype=np.float32
        )

        yrotmatrix = pyrr.matrix44.multiply(m1=transform, m2=rotationy)

        totalrotmatrix = pyrr.matrix44.multiply(m1=yrotmatrix, m2=rotationx)

        return totalrotmatrix


    # Move the user a certain direction based on direction facing
    def moveForward(self, angle):
        radian = -radians(angle)
        x = sin(radian) * self.moveSpeed
        z = cos(radian) * self.moveSpeed

        self.currPos[0] += -x
        self.currPos[2] += -z

        self.xUpdate += x
        self.zUpdate += z

    def moveBackward(self, angle):
        radian = -radians(angle)
        x = -sin(radian) * self.moveSpeed
        z = -cos(radian) * self.moveSpeed

        self.currPos[0] += -x
        self.currPos[2] += -z

        self.xUpdate += x
        self.zUpdate += z

    def moveRight(self, angle):
        radian = radians(90 - angle)
        x = -sin(radian) * self.moveSpeed
        z = -cos(radian) * self.moveSpeed

        self.currPos[0] += -x
        self.currPos[2] += -z

        self.xUpdate += x
        self.zUpdate += z

    def moveLeft(self, angle):
        radian = radians(90 - angle + 180)
        x = -sin(radian) * self.moveSpeed
        z = -cos(radian) * self.moveSpeed

        self.currPos[0] += -x
        self.currPos[2] += -z

        self.xUpdate += x
        self.zUpdate += z

    def quit(self):
        for object in self.objects:
            if object.name.lower().find("light") == -1:
                object.destroy()
        # glDeleteProgram(self.colorshader)
        glDeleteProgram(self.textureshader)
        pg.quit()
        exit(0)



if __name__ == "__main__":
    window = MainWindow(500, 500)

    window.run()
