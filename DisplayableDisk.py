"""
Define displayable cube here. Current version only use VBO
First version in 10/20/2021

:author: micou(Zezhou Sun)
:version: 2021.1.1
"""

from Displayable import Displayable
from GLBuffer import VAO, VBO, EBO
import numpy as np
import ColorType
import math

try:
    import OpenGL

    try:
        import OpenGL.GL as gl
        import OpenGL.GLU as glu
    except ImportError:
        from ctypes import util

        orig_util_find_library = util.find_library


        def new_util_find_library(name):
            res = orig_util_find_library(name)
            if res:
                return res
            return '/System/Library/Frameworks/' + name + '.framework/' + name


        util.find_library = new_util_find_library
        import OpenGL.GL as gl
        import OpenGL.GLU as glu
except ImportError:
    raise ImportError("Required dependency PyOpenGL not present")


class DisplayableDisk(Displayable):
    vao = None
    vbo = None
    ebo = None
    shaderProg = None

    vertices = None  # array to store vertices information
    indices = None  # stores triangle indices to vertices

    # stores current cube's information, read-only
    length = None
    width = None
    height = None
    color = None

    def __init__(self, shaderProg, radius, z, normal, slices=6, color=ColorType.BLUE):
        super(DisplayableDisk, self).__init__()
        self.shaderProg = shaderProg
        self.shaderProg.use()

        self.vao = VAO()
        self.vbo = VBO()  # vbo can only be initiate with glProgram activated
        self.ebo = EBO()

        self.generate(radius, z, normal, slices, color)

    def generate(self, radius, z, normal, slices, color=None):
        # self.length = length
        # self.width = width
        # self.height = height
        self.color = color
        pi = math.pi

        num_vertices = slices + 2 # when given = 30
        disk_vertices = np.zeros([num_vertices, 3])
        disk_normals = np.zeros([num_vertices, 3])

        for i, phi in enumerate(np.arange(-pi, pi + 2 * pi / slices, 2 * pi / slices)):
            x = radius * math.cos(phi)
            y = radius * math.sin(phi)

            disk_vertices[i] = [x, y, z]
            disk_normals[i] = [0, 0, normal]

        center = np.array([0, 0, z])
        triangle_list = []
        triangle_list.append(np.array([*center, 0, 0, normal, *color]))
        indices = []
        cidx = 1
        for i in range(slices + 1):
            triangle_list.append(np.array([disk_vertices[i][0], disk_vertices[i][1], disk_vertices[i][2],
                                           disk_normals[i][0], disk_normals[i][1], disk_normals[i][2], *color]))
            if (i < slices):
                indices.extend([0, cidx, cidx+1])
                cidx += 1
            elif (i == slices):
                indices.extend([0, cidx, 1])


        new_vl = np.stack(triangle_list)


        self.vertices = np.zeros([len(new_vl), 11])
        self.vertices[0:len(new_vl), 0:9] = new_vl



        self.indices = np.asarray(indices)

        # print(len(self.vertices), len(self.indices))


        # self.indices = np.zeros(0)

    def draw(self):
        self.vao.bind()
        self.ebo.draw()
        self.vao.unbind()

    def initialize(self):
        """
        Remember to bind VAO before this initialization. If VAO is not bind, program might throw an error
        in systems that don't enable a default VAO after GLProgram compilation
        """
        self.vao.bind()
        self.vbo.setBuffer(self.vertices, 11)
        self.ebo.setBuffer(self.indices)

        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexPos"),
                                  stride=11, offset=0, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexNormal"),
                                  stride=11, offset=3, attribSize=3)
        self.vbo.setAttribPointer(self.shaderProg.getAttribLocation("vertexColor"),
                                  stride=11, offset=6, attribSize=3)
        # TODO/BONUS 6.1 is at here, you need to set attribPointer for texture coordinates
        # you should check the corresponding variable name in GLProgram and set the pointer
        self.vao.unbind()

