"""
Define a class to store light information
First version in 11/08/2021

:author: micou(Zezhou Sun)
:version: 2021.1.1
"""

import numpy as np

from Point import Point


class Light:
    position = None
    color = None

    infiniteOn = False
    infiniteDirection = None

    spotOn = None
    spotDirection = None
    spotRadialFactor = None
    spotAngleLimit = None
    a_L = None

    isOn = True

    def __init__(self, position=None, color=None, infiniteDirection=None,
                 spotDirection=None, spotRadialFactor=None, spotAngleLimit=0, a_L=1):
        # set basic light
        if position is not None:
            self.setPosition(position)
        else:
            self.position = np.array((0, 0, 0))
        if color is not None:
            self.setColor(color)
        else:
            self.color = np.array((0, 0, 0, 0))

        # init radial attenuation parameters
        if infiniteDirection is not None:
            self.radialOn = True
            self.setInfiniteDirection(infiniteDirection)
        else:
            self.radialOn = False
            self.infiniteDirection = np.array((0, 0, 0))

        # init spot light parameters
        if spotDirection is not None:
            self.spotOn = True
            self.setSpotDirection(spotDirection)

            #self.setSpotRadialFactor(spotRadialFactor if (spotDirection is not None) else np.array((0, 0, 0)))
            self.setSpotRadialFactor(spotRadialFactor)
            self.a_L = a_L
        else:
            self.spotOn = False
            self.spotDirection = np.array((0, 0, 0))
            self.setSpotRadialFactor(np.array((0,0,0)))
            self.a_L = 0
        self.setSpotAngleLimit(spotAngleLimit)

    def __repr__(self):
        return f"pos: {self.position}, color:{self.color},\
        {self.infiniteOn},{self.infiniteDirection},\
        {self.spotOn},{self.spotDirection}, {self.spotRadialFactor},{self.spotAngleLimit},{self.a_L}, {self.isOn}"

    def setColor(self, color):
        if (not isinstance(color, np.ndarray)) or color.size != 4:
            raise TypeError("color must be a size 4 ndarray")
        self.color = color

    def setPosition(self, position):
        if (not isinstance(position, np.ndarray)) and (not isinstance(position, Point)):
            raise TypeError("position must be ndarray/Point")
        if isinstance(position, np.ndarray):
            if position.size != 3:
                raise TypeError("position must be a size 3 ndarray")
            self.position = position
        if isinstance(position, Point):
            if position.coords.size != 3:
                raise TypeError("position must be a size 3 Point")
            self.position = position.coords

    def setInfiniteDirection(self, infiniteDirection):
        if (not isinstance(infiniteDirection, np.ndarray)) and (not isinstance(infiniteDirection, Point)):
            raise TypeError("infiniteDirection must be ndarray/Point")
        if isinstance(infiniteDirection, np.ndarray):
            if infiniteDirection.size != 3:
                raise TypeError("infiniteDirection must be a size 3 ndarray")
            self.position = infiniteDirection
        if isinstance(infiniteDirection, Point):
            if infiniteDirection.coords.size != 3:
                raise TypeError("infiniteDirection must be a size 3 Point")
            self.position = infiniteDirection.coords

    def setSpotRadialFactor(self, spotRadialFactor):
        if (not isinstance(spotRadialFactor, np.ndarray)) or spotRadialFactor.size != 3:
            raise TypeError("spotRadialFactor must be a size 3 ndarray")
        self.spotRadialFactor = spotRadialFactor

    def setSpotAngleLimit(self, spotAngleLimit):
        if type(spotAngleLimit) != (int or float):
            raise TypeError("spotAngleLimit must be a int/float")
        self.spotAngleLimit = spotAngleLimit

    def setSpotDirection(self, spotDirection):
        if (not isinstance(spotDirection, np.ndarray)) and (not isinstance(spotDirection, Point)):
            raise TypeError("spotDirection must be ndarray/Point")
        if isinstance(spotDirection, np.ndarray):
            if spotDirection.size != 3:
                raise TypeError("spotDirection must be a size 3 ndarray")
            self.spotDirection = spotDirection
        if isinstance(spotDirection, Point):
            if spotDirection.coords.size != 3:
                raise TypeError("spotDirection must be a size 3 Point")
            self.spotDirection = spotDirection.coords
