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
from DisplayableSphere import DisplayableSphere
from DisplayableTorus import DisplayableTorus
from DisplayableEllipsoid import DisplayableEllipsoid
from DisplayableCylinder import DisplayableCylinder
from DisplayableDisk import DisplayableDisk

class SceneFour(Component, Animation):
    lights = None
    lightCubes = None
    shaderProg = None
    glutility = None

    lRadius = None
    lAngles = None
    lTransformations = None

    def __init__(self, shaderProg):
        super().__init__(Point((0, 0, 0)))
        self.shaderProg = shaderProg
        self.glutility = GLUtility.GLUtility()

        self.lTransformations = [self.glutility.translate(0, 2, 0, False),
                                 self.glutility.rotate(60, [0, 0, 1], False),
                                 self.glutility.rotate(120, [0, 0, 1], False)]
        self.lRadius = 3
        self.lAngles = [0, 0, 0]

        cube = Component(Point((-1.5, 0, 0)), DisplayableCube(shaderProg))
        cylinder = Component(Point((0, 0, -1)), DisplayableCylinder(shaderProg, 0.5, 2, 32, 32))
        cylinder.addChild(Component(Point((0,0,-1)), DisplayableDisk(shaderProg, 0.5, 1, -1, 32)))
        cylinder.addChild(Component(Point((0,0,1)), DisplayableDisk(shaderProg, 0.5, 1, 1, 32)))




        mCube = Material(np.array((0.01, 0.01, 0.01, 0.1)), np.array((0.2, 0.2, 0.2, 1)),
                      np.array((0.1, 0.1, 0.1, 0.1)), 13)
        mEllips = Material(np.array((0.01, 0.01, 0.01, 0.1)), np.array((0.3, 0.3, 0.3, 1)),
                      np.array((0.01, 0.2, 0.01, 0.1)), 20)
        mCylinder = Material(np.array((0.1, 0.1, 0.1, 0.1)), np.array((0.2, 0.2, 0.2, 1)),
                      np.array((0.4, 0.4, 0.4, 0.1)), 64)

        cube.setMaterial(mCube)
        # FROM LAB: original = "lighting" ... COLOR CHANGE
        cube.renderingRouting = "lighting"
        self.addChild(cube)

        cylinder.setMaterial(mCylinder)
        cylinder.renderingRouting = "lighting"
        for c in cylinder.children:
            c.setMaterial(mCylinder)
            c.renderingRouting = "lighting"
        self.addChild(cylinder)

        ellips = Component(Point((1.5, 0, 0)), DisplayableEllipsoid(shaderProg, 0.5, 0.5, .5, 32, 32, ColorType.PINK))
        ellips.setMaterial(mEllips)
        ellips.renderingRouting = "lighting"
        # torus.rotate(90, torus.uAxis)
        self.addChild(ellips)

        l0 = Light(self.lightPos(self.lRadius, self.lAngles[0], self.lTransformations[0]),
                   np.array((*ColorType.SOFTRED, .5)))
        lightCube0 = Component(Point((0, -1, 0)), DisplayableCube(shaderProg, 0.1, 0.1, 0.1, ColorType.SOFTRED))
        lightCube0.renderingRouting = "vertex"
        l1 = Light(self.lightPos(self.lRadius, self.lAngles[1], self.lTransformations[1]),
                   np.array((*ColorType.SOFTBLUE, 1.0)))
        # lightCube1 = Component(Point((0, 0, 0)), DisplayableCube(shaderProg, 0.1, 0.1, 0.1, ColorType.SOFTBLUE))
        # lightCube1.renderingRouting = "vertex"
        infinite_light = Light( Point((0, 5, 0)), np.array((*ColorType.YELLOW, .5)), infiniteDirection=np.array([0, 1, 0]))

        spot_light = Light(self.lightPos(.2, self.lAngles[0], self.lTransformations[0]),
                           np.array((*ColorType.SOFTGREEN, 1.0)),
                spotDirection=np.array([0, -1, 0]), spotAngleLimit=180, spotRadialFactor=np.array([0.01, 0.1, 0]), a_L=5 )
        spot_cube = Component(Point((0, 1, 0)), DisplayableEllipsoid(shaderProg, .4, .2, .4, color=ColorType.SOFTGREEN))
        spot_cube.renderingRouting = "vertex"

        spot_light1 = Light(self.lightPos(.3, self.lAngles[0], self.lTransformations[0]),
                           np.array((*ColorType.GREEN, 1.0)),
                           spotDirection=np.array([-.5, -1, 0]), spotAngleLimit=80,
                           spotRadialFactor=np.array([.1, 0, 0.1]), a_L=.5)
        spot_cube1 = Component(Point((0, 1, 0)), DisplayableEllipsoid(shaderProg, .4, .2, .4, color=ColorType.GREEN))
        spot_cube1.renderingRouting = "vertex"

        # lightCube2 = Component(Point((0, 5, 0)), DisplayableCube(shaderProg, 0.1, 0.1, 0.1, ColorType.PINK))
        # lightCube2.renderingRouting = "vertex"

        self.addChild(lightCube0)
        # self.addChild(lightCube1)
        self.addChild(spot_cube)
        self.addChild(spot_cube1)
        self.lights = [spot_light, l0, spot_light1, infinite_light]
        self.lightCubes = [spot_cube, lightCube0, spot_cube1]

    def lightPos(self, radius, thetaAng, transformationMatrix):
        r = np.zeros(4)
        r[0] = radius * math.cos(thetaAng / 180 * math.pi)
        r[2] = radius * math.sin(thetaAng / 180 * math.pi)
        r[3] = 1
        r = transformationMatrix @ r
        return r[0:3]

    def animationUpdate(self):
        self.lAngles[0] = (self.lAngles[0] + 0.5) % 360
        self.lAngles[1] = (self.lAngles[1] + 0.7) % 360
        self.lAngles[2] = (self.lAngles[2] + 1.0) % 360
        for i, v in enumerate(self.lights):
            if i != len(self.lights) - 1:
                lPos = self.lightPos(self.lRadius, self.lAngles[i], self.lTransformations[i])
                self.lightCubes[i].setCurrentPosition(Point(lPos))
                self.lights[i].setPosition(lPos)
                self.shaderProg.setLight(i, v)

        for c in self.children:
            if isinstance(c, Animation):
                c.animationUpdate()

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
