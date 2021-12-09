"""
Define displayable cube here. Current version only use VBO
First version in 10/20/2021

:author: micou(Zezhou Sun)
:version: 2021.1.1
"""

from Displayable import Displayable
from DisplayableDisk import DisplayableDisk
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


class DisplayableCylinder(Displayable):
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

    end1 = None
    end2 = None

    def __init__(self, shaderProg, endRadius, height, slices=6, stacks=6, color=ColorType.BLUE):
        super(DisplayableCylinder, self).__init__()
        self.shaderProg = shaderProg
        self.shaderProg.use()

        self.vao = VAO()
        self.vbo = VBO()  # vbo can only be initiate with glProgram activated
        self.ebo = EBO()

        #self.end1 = DisplayableDisk(shaderProg, endRadius, 0, -1, slices, color)
        self.generate(endRadius, height, slices, stacks, color)
        #self.end2 = DisplayableDisk(shaderProg, endRadius, height, 1,  slices, color)
    #                   slices=segments in circles, stacks=segments in tube (height)
    def generate(self, endRadius, height, slices=6, stacks=6, color=None):
        # self.length = length
        # self.width = width
        self.height = height
        self.color = color
        pi = math.pi

        num_divisions = (slices) * (stacks)   # when given = 30
        num_end_vertices = 2 * (slices + 2)     # For disk

        cylinder_vertices = np.zeros([num_divisions+1, num_divisions+1, 3])
        cylinder_normals = np.zeros([num_divisions+1, num_divisions+1, 3])


        #                       np.arrange(start, stop, step increment)
        for i, current_h in enumerate(np.arange(0, height + height/stacks, height/stacks)):
            for j, theta in enumerate(np.arange(-pi, pi + 2 * pi / slices, 2 * pi / slices)):

                x = endRadius * math.cos(theta)
                y = endRadius * math.sin(theta)
                z = current_h

                x_normal = math.cos(theta)
                y_normal = math.sin(theta)
                z_normal = 0

                cylinder_vertices[i][j] = [x, y, z]
                cylinder_normals[i][j] = [x_normal, y_normal, z_normal]


        indices = []
        cidx = 0

        triangle_list = []
        for i in range(stacks+1):
            for j in range(slices+1):

                triangle_list.append(np.array([
                    cylinder_vertices[i][j][0], cylinder_vertices[i][j][1], cylinder_vertices[i][j][2],
                    cylinder_normals[i][j][0], cylinder_normals[i][j][1], cylinder_normals[i][j][2], *color]))

                if (i < stacks and j < slices):
                    indices.extend([
                        cidx, cidx + 1, cidx + 1 + slices,
                        cidx, cidx + slices, cidx + 1 + slices
                    ])

                elif (i == stacks and j < slices):
                    indices.extend([
                        cidx, cidx + 1, j + 1,
                        cidx, j, j + 1
                    ])

                elif (i < stacks and j == slices):
                    indices.extend([
                        cidx, cidx - j, cidx - (slices - j),
                        cidx, cidx + slices, cidx - slices + j
                    ])

                elif (i == stacks and j == slices):
                    indices.extend([
                        cidx, cidx - j, 0,
                        cidx, j, 0
                    ])
                cidx += 1

        new_vl = np.stack(triangle_list)

        self.vertices = np.zeros([len(new_vl), 11])
        self.vertices[0:len(new_vl), 0:9] = new_vl


        self.indices = np.asarray(indices)
        #print(len(new_vl), len(self.indices))


        # self.indices = np.zeros(0)

    def draw(self):
        self.vao.bind()
        self.ebo.draw()
        self.vao.unbind()
        #self.end1.draw()
        #self.end2.draw()


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

        #self.end1.initialize()
        #self.end2.initialize()

