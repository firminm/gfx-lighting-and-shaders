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


class DisplayableEllipsoid(Displayable):
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

    def __init__(self, shaderProg, rx=1, ry=1, rz=1, slices=12, stacks=12, color=ColorType.BLUE):
        super(DisplayableEllipsoid, self).__init__()
        self.shaderProg = shaderProg
        self.shaderProg.use()

        self.vao = VAO()
        self.vbo = VBO()  # vbo can only be initiate with glProgram activated
        self.ebo = EBO()

        self.generate(rx, ry, rz, slices, stacks, color)

    def generate(self, rx=1, ry=1, rz=1, slices=6, stacks=6, color=None):
        # self.length = length
        # self.width = width
        # self.height = height
        self.color = color
        pi = math.pi

        num_divisions = slices * (stacks-1) # when given = 30
        ellipsoid_vertices = np.zeros([stacks+1, slices+1, 3])
        ellipsoid_normals = np.zeros([stacks+1, slices+1, 3])

        for i, phi in enumerate(np.arange(-pi/2, pi/2 + pi/stacks, pi/stacks)):
            for j, theta in enumerate(np.arange(-pi, pi + 2 * pi / slices, 2 * pi / slices)):
                if rz == 0:
                    x = rx * math.cos(theta)
                    y = ry * math.sin(theta)
                    z = 0
                else:
                    x = rx * math.cos(phi) * math.cos(theta)
                    y = ry * math.cos(phi) * math.sin(theta)
                    z = rz * math.sin(phi)

                x_normal = math.cos(phi) * math.cos(theta) / rx
                y_normal = math.cos(phi) * math.sin(theta) / ry
                z_normal = math.sin(phi) / rz

                ellipsoid_vertices[i][j] = [x, y, z]
                ellipsoid_normals[i][j] = [x_normal, y_normal, z_normal]

        indices = []
        cidx = 0

        triangle_list = []
        for i in range(stacks + 1):
            for j in range(slices + 1):
                triangle_list.append(np.array([
                    ellipsoid_vertices[i][j][0], ellipsoid_vertices[i][j][1], ellipsoid_vertices[i][j][2],
                    ellipsoid_normals[i][j][0], ellipsoid_normals[i][j][1], ellipsoid_normals[i][j][2], *color]))

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
                        cidx, cidx - j, cidx + slices - j + 1,
                        cidx, cidx + slices, cidx + slices - j + 1
                    ])

                elif (i == stacks and j == slices):
                    indices.extend([
                        cidx, cidx - j, 0,
                        cidx, j, 0
                    ])
                cidx += 1
                '''
                if (i < slices and j < stacks):
                    triangle_list.append(np.array([ellipsoid_vertices[i][j][0], ellipsoid_vertices[i][j][1]
                                                      , ellipsoid_vertices[i][j][2], ellipsoid_normals[i][j][0],
                                                   ellipsoid_normals[i][j][1]
                                                      , ellipsoid_normals[i][j][2], *color]))   # vert 0
                    triangle_list.append(np.array([ellipsoid_vertices[i][j + 1][0], ellipsoid_vertices[i][j + 1][1],
                                                   ellipsoid_vertices[i][j + 1][2], ellipsoid_normals[i][j + 1][0],
                                                   ellipsoid_normals[i][j + 1][1],
                                                   ellipsoid_normals[i][j + 1][2], *color]))    # vert 1
                    triangle_list.append(np.array([ellipsoid_vertices[i + 1][j + 1][0], ellipsoid_vertices[i + 1][j + 1][1],
                                                   ellipsoid_vertices[i + 1][j + 1][2], ellipsoid_normals[i + 1][j + 1][0],
                                                   ellipsoid_normals[i + 1][j + 1][1],
                                                   ellipsoid_normals[i + 1][j + 1][2], *color]))    # vert 2

                    # triangle_list.append(np.array([ellipsoid_vertices[i][j][0], ellipsoid_vertices[i][j][1]
                    #                                   , ellipsoid_vertices[i][j][2], ellipsoid_normals[i][j][0],
                    #                                ellipsoid_normals[i][j][1]
                    #                                   , ellipsoid_normals[i][j][2], *color]))   # vert 0
                    triangle_list.append(np.array([ellipsoid_vertices[i + 1][j][0], ellipsoid_vertices[i + 1][j][1],
                                                   ellipsoid_vertices[i + 1][j][2], ellipsoid_normals[i + 1][j][0],
                                                   ellipsoid_normals[i + 1][j][1],
                                                   ellipsoid_normals[i + 1][j][2], *color]))    # vert 3
                    # triangle_list.append(np.array([ellipsoid_vertices[i + 1][j + 1][0], ellipsoid_vertices[i + 1][j + 1][1],
                    #                                ellipsoid_vertices[i + 1][j + 1][2], ellipsoid_normals[i + 1][j + 1][0],
                    #                                ellipsoid_normals[i + 1][j + 1][1],
                    #                                ellipsoid_normals[i + 1][j + 1][2], *color]))    # vert 2


                elif (i == slices and j < stacks):
                    triangle_list.append(np.array([ellipsoid_vertices[i][j][0], ellipsoid_vertices[i][j][1]
                                                      , ellipsoid_vertices[i][j][2], ellipsoid_normals[i][j][0],
                                                   ellipsoid_normals[i][j][1]
                                                      , ellipsoid_normals[i][j][2], *color]))   # vert 0
                    triangle_list.append(np.array([ellipsoid_vertices[i][j + 1][0], ellipsoid_vertices[i][j + 1][1],
                                                   ellipsoid_vertices[i][j + 1][2], ellipsoid_normals[i][j + 1][0],
                                                   ellipsoid_normals[i][j + 1][1],
                                                   ellipsoid_normals[i][j + 1][2], *color]))    # vert 1
                    triangle_list.append(np.array([ellipsoid_vertices[0][j + 1][0], ellipsoid_vertices[0][j + 1][1],
                                                   ellipsoid_vertices[0][j + 1][2], ellipsoid_normals[0][j + 1][0],
                                                   ellipsoid_normals[0][j + 1][1],
                                                   ellipsoid_normals[0][j + 1][2], *color]))    # vert 2

                    # triangle_list.append(np.array([ellipsoid_vertices[i][j][0], ellipsoid_vertices[i][j][1]
                    #                                   , ellipsoid_vertices[i][j][2], ellipsoid_normals[i][j][0],
                    #                                ellipsoid_normals[i][j][1]
                    #                                   , ellipsoid_normals[i][j][2], *color]))   # vert 0
                    triangle_list.append(np.array([ellipsoid_vertices[0][j][0], ellipsoid_vertices[0][j][1],
                                                   ellipsoid_vertices[0][j][2], ellipsoid_normals[0][j][0],
                                                   ellipsoid_normals[0][j][1],
                                                   ellipsoid_normals[0][j][2], *color]))
                    # triangle_list.append(np.array([ellipsoid_vertices[0][j + 1][0], ellipsoid_vertices[0][j + 1][1],
                    #                                ellipsoid_vertices[0][j + 1][2], ellipsoid_normals[0][j + 1][0],
                    #                                ellipsoid_normals[0][j + 1][1],
                    #                                ellipsoid_normals[0][j + 1][2], *color]))    # vert 2


                elif (i < slices and j == stacks):
                    triangle_list.append(np.array([ellipsoid_vertices[i][j][0], ellipsoid_vertices[i][j][1]
                                                      , ellipsoid_vertices[i][j][2], ellipsoid_normals[i][j][0],
                                                   ellipsoid_normals[i][j][1]
                                                      , ellipsoid_normals[i][j][2], *color]))   # vert 0
                    triangle_list.append(np.array([ellipsoid_vertices[i][0][0], ellipsoid_vertices[i][0][1],
                                                   ellipsoid_vertices[i][0][2], ellipsoid_normals[i][0][0],
                                                   ellipsoid_normals[i][0][1],
                                                   ellipsoid_normals[i][0][2], *color]))        # Vert 1
                    triangle_list.append(np.array([ellipsoid_vertices[i + 1][0][0], ellipsoid_vertices[i + 1][0][1],
                                                   ellipsoid_vertices[i + 1][0][2], ellipsoid_normals[i + 1][0][0],
                                                   ellipsoid_normals[i + 1][0][1],
                                                   ellipsoid_normals[i + 1][0][2], *color]))    # vert 2

                    # triangle_list.append(np.array([ellipsoid_vertices[i][j][0], ellipsoid_vertices[i][j][1]
                    #                                   , ellipsoid_vertices[i][j][2], ellipsoid_normals[i][j][0],
                    #                                ellipsoid_normals[i][j][1]
                    #                                   , ellipsoid_normals[i][j][2], *color]))   # vert 0
                    triangle_list.append(np.array([ellipsoid_vertices[i + 1][j][0], ellipsoid_vertices[i + 1][j][1],
                                                   ellipsoid_vertices[i + 1][j][2], ellipsoid_normals[i + 1][j][0],
                                                   ellipsoid_normals[i + 1][j][1],
                                                   ellipsoid_normals[i + 1][j][2], *color]))    # vert 3
                    # triangle_list.append(np.array([ellipsoid_vertices[i + 1][0][0], ellipsoid_vertices[i + 1][0][1],
                    #                                ellipsoid_vertices[i + 1][0][2], ellipsoid_normals[i + 1][0][0],
                    #                                ellipsoid_normals[i + 1][0][1],
                    #                                ellipsoid_normals[i + 1][0][2], *color]))    # vert 2

                elif (i == slices and j == stacks):
                    triangle_list.append(np.array([ellipsoid_vertices[i][j][0], ellipsoid_vertices[i][j][1]
                                                      , ellipsoid_vertices[i][j][2], ellipsoid_normals[i][j][0],
                                                   ellipsoid_normals[i][j][1]
                                                      , ellipsoid_normals[i][j][2], *color]))   # vert 0
                    triangle_list.append(np.array([ellipsoid_vertices[i][0][0], ellipsoid_vertices[i][0][1],
                                                   ellipsoid_vertices[i][0][2], ellipsoid_normals[i][0][0],
                                                   ellipsoid_normals[i][0][1],
                                                   ellipsoid_normals[i][0][2], *color]))        # vert 1
                    triangle_list.append(np.array([ellipsoid_vertices[0][0][0], ellipsoid_vertices[0][0][1],
                                                   ellipsoid_vertices[0][0][2], ellipsoid_normals[0][0][0],
                                                   ellipsoid_normals[0][0][1],
                                                   ellipsoid_normals[0][0][2], *color]))        # vert 2

                    # triangle_list.append(np.array([ellipsoid_vertices[i][j][0], ellipsoid_vertices[i][j][1]
                    #                                   , ellipsoid_vertices[i][j][2], ellipsoid_normals[i][j][0],
                    #                                ellipsoid_normals[i][j][1]
                    #                                   , ellipsoid_normals[i][j][2], *color]))   # vert 0
                    triangle_list.append(np.array([ellipsoid_vertices[0][j][0], ellipsoid_vertices[0][j][1],
                                                   ellipsoid_vertices[0][j][2], ellipsoid_normals[0][j][0],
                                                   ellipsoid_normals[0][j][1],
                                                   ellipsoid_normals[0][j][2], *color]))
                    # triangle_list.append(np.array([ellipsoid_vertices[0][0][0], ellipsoid_vertices[0][0][1],
                    #                                ellipsoid_vertices[0][0][2], ellipsoid_normals[0][0][0],
                    #                                ellipsoid_normals[0][0][1],
                    #                                ellipsoid_normals[0][0][2], *color]))        # vert 2

                indices.extend([cidx, cidx + 1, cidx + 2, cidx, cidx + 3, cidx + 2])
                cidx += 4
                '''

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

