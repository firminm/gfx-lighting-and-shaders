"""
Define a fixed scene with rotating lights
First version in 11/08/2021

:author: micou(Zezhou Sun)
:version: 2021.1.1
"""
import math

import numpy as np

import ColorType
from Animation import Animation
from Component import Component
from Light import Light
from Material import Material
from Point import Point
import GLUtility

from DisplayableCube import DisplayableCube
from DisplayableTorus import DisplayableTorus
from DisplayableSphere import DisplayableSphere
from DisplayableEllipsoid import DisplayableEllipsoid
from DisplayableCylinder import DisplayableCylinder


##### TODO 1: Generate Triangle Meshes
# Requirements:
#   1. Use Element Buffer Object (EBO) to draw the cube. The cube provided in the start code is drawn with Vertex Buffer
#   Object (VBO). In the DisplayableCube class draw method, you should switch from VBO draw to EBO draw. To achieve
#   this, please first read through VBO and EBO classes in GLBuffer. Then you rewrite the self.vertices and self.indices
#   in the DisplayableCube class. Once you have all these down, then switch the line vbo.draw() to ebo.draw().
#   2. Generate Displayable classes for an ellipsoid, torus, and cylinder with end caps.
#   These classes should be like the DisplayableCube class and they should all use EBO in the draw method.
#   PS: You must use the ellipsoid formula to generate it, scaling the Displayable sphere doesn't count
#
#   Displayable object's self.vertices numpy matrix should be defined as this table:
#   Column | 0:3                | 3:6           | 6:9          | 9:11
#   Stores | Vertex coordinates | Vertex normal | Vertex Color | Vertex texture Coordinates
#
#   Their __init__ method should accept following input
#   arguments:
#   DisplayableEllipsoid(radiusInX, radiusInY, radiusInZ, slices, stacks)
#   DisplayableTorus(innerRadius, outerRadius, nsides, rings)
#   DisplayableCylinder(endRadius, height, slices, stacks)
#

##### TODO 5: Create your scenes
# Requirements:
#   1. We provide a fixed scene (SceneOne) for you with preset lights, material, and model parameters.
#   This scene will be used to examine your illumination implementation, and you should not modify it.
#   2. Create 3 new scenes (can be static scenes). Each of your scenes must have
#      * at least 3 differently shaped solid objects
#      * each object should have a different material
#      * at least 2 lights
#      * All types of lights should be used
#   3. Provide a keyboard interface that allows the user to toggle on/off each of the lights in your scene model:
#   Hit 1, 2, 3, 4, etc. to identify which light to toggle.


class SceneTwo(Component):
    shaderProg = None
    glutility = None

    lights = None
    lightCubes = None

    # specularOn = True
    # diffuseOn = True
    # ambientOn = True

    def __init__(self, shaderProg):
        super().__init__(Point((0, 0, 0)))
        self.shaderProg = shaderProg
        self.glutility = GLUtility.GLUtility()
        # self.shaderProg.setSpecular(self.specularOn)
        # self.shaderProg.setDiffuse(self.diffuseOn)
        # self.shaderProg.setAmbient(self.ambientOn)


        # cube1 = Component(Point((0, 0, 0)), DisplayableCylinder(shaderProg, 0.5, 1, 6, 6))

        cube1 = Component(Point((0, 0, 0)), DisplayableEllipsoid(shaderProg, 1.0, 1, 1, 12, 12))
        cube2 = Component(Point((-2, 0, 0)), DisplayableEllipsoid(shaderProg, 1.0, .5, 1))
        cube3 = Component(Point((2, 0, 0)), DisplayableEllipsoid(shaderProg, 1, .25, .5, 32, 32))

        m1 = Material(np.array((0.1, 0.1, 0.1, 0.1)), np.array((0.2, 0.2, 0.2, 1)), # Reg
                      np.array((0.4, 0.4, 0.4, 1)), 1)
        m2 = Material(np.array((0.1, 0.1, 0.1, 0.1)), np.array((0.2, 0.2, 0.2, 1)), # Only diffuse (no spec) LEFT
                 np.array((0., 0., 0., 0)), 32)
        m3 = Material(np.array((0.1, 0.1, 0.1, 0.1)), np.array((0, 0, 0, 1)),       # Only spec (no diffuse) RIGHT
                 np.array((0.4, 0.4, 0.4, 1)), 12)
        cube1.setMaterial(m1)
        cube2.setMaterial(m2)
        cube3.setMaterial(m3)

        cube1.renderingRouting = "lighting"
        cube2.renderingRouting = "lighting"
        cube3.renderingRouting = "lighting"

        self.addChild(cube1)
        self.addChild(cube2)
        self.addChild(cube3)


        l0 = Light(Point([1, 2, 0.0]), np.array((*ColorType.PURPLE, 1.0)),
                   spotDirection=np.array([-1, -2, 0]), spotAngleLimit=10, spotRadialFactor=np.array([1, 1, 10]), a_L=5 )
        # l0 = Light(Point([0.0, 4, 0.0]), np.array((*ColorType.RED, 1.0)))
        lightCube0 = Component(Point((1, 2, 0.0)), DisplayableCube(shaderProg, 0.1, 0.1, 0.1, ColorType.PURPLE))
        lightCube0.renderingRouting = "vertex"

        l1 = Light(Point([-1, 2, 0.0]), np.array((*ColorType.GREEN, 1.0)))     # regular
        lightCube1 = Component(Point((-1, 2, 0.0)), DisplayableCube(shaderProg, 0.1, 0.1, 0.1, ColorType.GREEN))
        lightCube1.renderingRouting = "vertex"

        l2 = Light(Point([-1.5, -3, 0.0]), np.array((*ColorType.SOFTBLUE, 1.0)),   # infinite
                   infiniteDirection=np.array([-2, -10, 0]))
        lightCube2 = Component(Point((-1.5, -3, 0.0)), DisplayableCube(shaderProg, .1, .1, .1, ColorType.SOFTBLUE))
        lightCube2.renderingRouting = "vertex"


        self.addChild(lightCube0)
        self.addChild(lightCube1)
        self.addChild(lightCube2)

        self.lights = [l0, l1, l2]
        self.lightCubes = [lightCube0, lightCube1, lightCube2 ]

    def initialize(self):
        self.shaderProg.clearAllLights()
        for i, v in enumerate(self.lights):
            self.shaderProg.setLight(i, v)
        super().initialize()

    def toggle_light(self, light_index):
        if light_index > len(self.lights):
            print(f"Invalid index, {len(self.lights)} lights")
        else:
            self.lights[light_index-1].isOn = not self.lights[light_index-1].isOn
            self.shaderProg.setLight(light_index-1, self.lights[light_index-1])

    # def toggle_light_style(self, specular=False, diffuse=False, ambient=False):
    #     if specular:
    #         self.specularOn = not self.specularOn
    #         self.shaderProg.setSpecular(self.specularOn)
    #     elif diffuse:
    #         self.diffuseOn = not self.diffuseOn
    #         self.shaderProg.setDiffuse(self.diffuseOn)
    #     elif ambient:
    #         self.ambientOn = not self.ambientOn
    #         self.shaderProg.setAmbient(self.ambientOn)
    #
    #
