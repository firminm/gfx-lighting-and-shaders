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

class SceneFive(Component, Animation):
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

        cube = Component(Point((-2, 0, 0)), DisplayableSphere(shaderProg, 1.0))
        cube = Component(Point((0, 0, 1)), DisplayableCube(shaderProg))
        cylinder = Component(Point((0, 0, -1)), DisplayableCylinder(shaderProg, 0.5, 2, 6, 6, color=ColorType.DARKORANGE1))
        # cube2 = Component(Point((-1, 0, 0)), DisplayableDisk(shaderProg, 0.5, 1, 1, 30))



        mCylinder = Material(np.array((0.1, 0.1, 0.1, 0.1)), np.array((0.2, 0.2, 0.2, 1)),
                      np.array((0.4, 0.4, 0.4, 0.1)), 63)
        m2 = Material(np.array((0.1, 0.1, 0.1, 0.1)), np.array((0.2, 0.2, 0.2, 1)),
                      np.array((0.4, 0.4, 0.4, 0.1)), 15)
        m3 = Material(np.array((0.1, 0.1, 0.1, 0.1)), np.array((0.2, 0.2, 0.2, 1)),
                      np.array((0.4, 0.4, 0.4, 0.1)), 64)
        cube.setMaterial(m2)

        # FROM LAB: original = "lighting" ... COLOR CHANGE
        cube.renderingRouting = "lighting"

        cube2 = Component(Point((1, 0, 0)), DisplayableEllipsoid(shaderProg, 1, 1, 1, 30, 30))
        cube2.setMaterial(m2)
        cube2.renderingRouting = "lighting"
        # self.addChild(cube2)

        cylinder.setMaterial(mCylinder)
        cylinder.renderingRouting = "lighting"

        cylinder.addChild(Component(Point((0, 0, -1)), DisplayableDisk(shaderProg, 0.5, 1, -1, 6, color=ColorType.DARKORANGE1)))
        cylinder.addChild(Component(Point((0, 0, 1)), DisplayableDisk(shaderProg, 0.5, 1, 1, 6, color=ColorType.DARKORANGE1)))
        cylinder.addChild(cube)

        for c in cylinder.children:
            c.setMaterial(mCylinder)
            c.renderingRouting = "lighting"
        self.addChild(cylinder)

        cylinder.rotate(20, cylinder.uAxis)
        cylinder.rotate(45, cylinder.wAxis)

        torus = Component(Point((1, 0, 0)), DisplayableTorus(shaderProg, 0.25, 0.5, 36, 36))
        m2 = Material(np.array((0.1, 0.1, 0.1, 0.1)), np.array((0.2, 0.2, 0.2, 1)),
                      np.array((0, 0, 0, 1.0)), 32)
        torus.setMaterial(m2)
        torus.renderingRouting = "lighting"
        torus.rotate(90, torus.uAxis)
        self.addChild(torus)

        l0 = Light(self.lightPos(self.lRadius, self.lAngles[0], self.lTransformations[0]),
                   np.array((*ColorType.SOFTRED, 1.0)))
        lightCube0 = Component(Point((0, 0, 0)), DisplayableCube(shaderProg, 0.1, 0.1, 0.1, ColorType.SOFTRED))
        lightCube0.renderingRouting = "vertex"
        l1 = Light(self.lightPos(self.lRadius, self.lAngles[1], self.lTransformations[1]),
                   np.array((*ColorType.SOFTBLUE, 1.0)))
        lightCube1 = Component(Point((0, 0, 0)), DisplayableCube(shaderProg, 0.1, 0.1, 0.1, ColorType.SOFTBLUE))
        lightCube1.renderingRouting = "vertex"
        l2 = Light(self.lightPos(self.lRadius, self.lAngles[2], self.lTransformations[2]),
                   np.array((*ColorType.SOFTGREEN, 1.0)))
        lightCube2 = Component(Point((0, 0, 0)), DisplayableCube(shaderProg, 0.1, 0.1, 0.1, ColorType.SOFTGREEN))
        lightCube2.renderingRouting = "vertex"

        self.addChild(lightCube0)
        self.addChild(lightCube1)
        self.addChild(lightCube2)
        self.lights = [l0, l1, l2]
        self.lightCubes = [lightCube0, lightCube1, lightCube2]

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
