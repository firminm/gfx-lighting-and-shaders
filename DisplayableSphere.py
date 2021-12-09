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


class DisplayableSphere(Displayable):
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

    def __init__(self, shaderProg, radius=1, color=ColorType.BLUE):
        super(DisplayableSphere, self).__init__()
        self.shaderProg = shaderProg
        self.shaderProg.use()

        self.vao = VAO()
        self.vbo = VBO()  # vbo can only be initiate with glProgram activated
        self.ebo = EBO()

        self.generate(radius, color)

    def generate(self, radius=1, color=None):
        # self.length = length
        # self.width = width
        # self.height = height
        self.color = color
        pi = math.pi

        sphere_vertices = np.zeros([31,31,3])
        sphere_normals = np.zeros([31,31,3])
        for i,phi in enumerate(np.arange(-pi/2, pi/2 + pi/30, pi/30)):
            for j,theta in enumerate(np.arange(-pi, pi + pi/15, 2*pi/30)):
                x = radius*math.cos(phi)*math.cos(theta)
                y = radius*math.cos(phi)*math.sin(theta)
                z = radius*math.sin(phi)

                x_normal = math.cos(phi)*math.cos(theta)
                y_normal = math.cos(phi)*math.sin(theta)
                z_normal = math.sin(phi)

                sphere_vertices[i][j] = [x,y,z]
                sphere_normals[i][j] = [x_normal,y_normal,z_normal]

        triangle_list = []
        for i in range(31):
            for j in range(31):
                if(i<30 and j<30):
                    triangle_list.append(np.array([sphere_vertices[i][j][0],sphere_vertices[i][j][1]
                        ,sphere_vertices[i][j][2], sphere_normals[i][j][0],sphere_normals[i][j][1]
                        ,sphere_normals[i][j][2],*color]))
                    triangle_list.append(np.array([sphere_vertices[i][j+1][0],sphere_vertices[i][j+1][1],
                        sphere_vertices[i][j+1][2],sphere_normals[i][j+1][0],sphere_normals[i][j+1][1],
                        sphere_normals[i][j+1][2],*color]))
                    triangle_list.append(np.array([sphere_vertices[i+1][j+1][0],sphere_vertices[i+1][j+1][1],
                        sphere_vertices[i+1][j+1][2],sphere_normals[i+1][j+1][0],sphere_normals[i+1][j+1][1],
                        sphere_normals[i+1][j+1][2],*color]))

                    triangle_list.append(np.array([sphere_vertices[i][j][0],sphere_vertices[i][j][1]
                        ,sphere_vertices[i][j][2], sphere_normals[i][j][0],sphere_normals[i][j][1]
                        ,sphere_normals[i][j][2],*color]))
                    triangle_list.append(np.array([sphere_vertices[i+1][j][0],sphere_vertices[i+1][j][1],
                        sphere_vertices[i+1][j][2],sphere_normals[i+1][j][0],sphere_normals[i+1][j][1],
                        sphere_normals[i+1][j][2],*color]))
                    triangle_list.append(np.array([sphere_vertices[i+1][j+1][0],sphere_vertices[i+1][j+1][1],
                        sphere_vertices[i+1][j+1][2],sphere_normals[i+1][j+1][0],sphere_normals[i+1][j+1][1],
                        sphere_normals[i+1][j+1][2],*color]))
                elif(i==30 and j<30):
                    triangle_list.append(np.array([sphere_vertices[i][j][0],sphere_vertices[i][j][1]
                        ,sphere_vertices[i][j][2],sphere_normals[i][j][0],sphere_normals[i][j][1]
                        ,sphere_normals[i][j][2],*color]))
                    triangle_list.append(np.array([sphere_vertices[i][j+1][0],sphere_vertices[i][j+1][1],
                        sphere_vertices[i][j+1][2],sphere_normals[i][j+1][0],sphere_normals[i][j+1][1],
                        sphere_normals[i][j+1][2],*color]))
                    triangle_list.append(np.array([sphere_vertices[0][j+1][0],sphere_vertices[0][j+1][1],
                        sphere_vertices[0][j+1][2],sphere_normals[0][j+1][0],sphere_normals[0][j+1][1],
                        sphere_normals[0][j+1][2],*color]))

                    triangle_list.append(np.array([sphere_vertices[i][j][0],sphere_vertices[i][j][1]
                        ,sphere_vertices[i][j][2], sphere_normals[i][j][0],sphere_normals[i][j][1]
                        ,sphere_normals[i][j][2],*color]))
                    triangle_list.append(np.array([sphere_vertices[0][j][0],sphere_vertices[0][j][1],
                        sphere_vertices[0][j][2],sphere_normals[0][j][0],sphere_normals[0][j][1],
                        sphere_normals[0][j][2],*color]))
                    triangle_list.append(np.array([sphere_vertices[0][j+1][0],sphere_vertices[0][j+1][1],
                        sphere_vertices[0][j+1][2],sphere_normals[0][j+1][0],sphere_normals[0][j+1][1],
                        sphere_normals[0][j+1][2],*color]))
                elif(i<30 and j==30):
                    triangle_list.append(np.array([sphere_vertices[i][j][0],sphere_vertices[i][j][1]
                        ,sphere_vertices[i][j][2],sphere_normals[i][j][0],sphere_normals[i][j][1]
                        ,sphere_normals[i][j][2],*color]))
                    triangle_list.append(np.array([sphere_vertices[i][0][0],sphere_vertices[i][0][1],
                        sphere_vertices[i][0][2],sphere_normals[i][0][0],sphere_normals[i][0][1],
                        sphere_normals[i][0][2],*color]))
                    triangle_list.append(np.array([sphere_vertices[i+1][0][0],sphere_vertices[i+1][0][1],
                        sphere_vertices[i+1][0][2],sphere_normals[i+1][0][0],sphere_normals[i+1][0][1],
                        sphere_normals[i+1][0][2],*color]))

                    triangle_list.append(np.array([sphere_vertices[i][j][0],sphere_vertices[i][j][1]
                        ,sphere_vertices[i][j][2],sphere_normals[i][j][0],sphere_normals[i][j][1]
                        ,sphere_normals[i][j][2],*color]))
                    triangle_list.append(np.array([sphere_vertices[i+1][j][0],sphere_vertices[i+1][j][1],
                        sphere_vertices[i+1][j][2],sphere_normals[i+1][j][0],sphere_normals[i+1][j][1],
                        sphere_normals[i+1][j][2],*color]))
                    triangle_list.append(np.array([sphere_vertices[i+1][0][0],sphere_vertices[i+1][0][1],
                        sphere_vertices[i+1][0][2],sphere_normals[i+1][0][0],sphere_normals[i+1][0][1],
                        sphere_normals[i+1][0][2],*color]))
                elif (i==30 and j==30):
                    triangle_list.append(np.array([sphere_vertices[i][j][0],sphere_vertices[i][j][1]
                        ,sphere_vertices[i][j][2], sphere_normals[i][j][0],sphere_normals[i][j][1]
                        ,sphere_normals[i][j][2],*color]))
                    triangle_list.append(np.array([sphere_vertices[i][0][0],sphere_vertices[i][0][1],
                        sphere_vertices[i][0][2],sphere_normals[i][0][0],sphere_normals[i][0][1],
                        sphere_normals[i][0][2],*color]))
                    triangle_list.append(np.array([sphere_vertices[0][0][0],sphere_vertices[0][0][1],
                        sphere_vertices[0][0][2],sphere_normals[0][0][0],sphere_normals[0][0][1],
                        sphere_normals[0][0][2],*color]))

                    triangle_list.append(np.array([sphere_vertices[i][j][0],sphere_vertices[i][j][1]
                        ,sphere_vertices[i][j][2], sphere_normals[i][j][0],sphere_normals[i][j][1]
                        ,sphere_normals[i][j][2],*color]))
                    triangle_list.append(np.array([sphere_vertices[0][j][0],sphere_vertices[0][j][1],
                        sphere_vertices[0][j][2],sphere_normals[0][j][0],sphere_normals[0][j][1],
                        sphere_normals[0][j][2],*color]))
                    triangle_list.append(np.array([sphere_vertices[0][0][0],sphere_vertices[0][0][1],
                        sphere_vertices[0][0][2],sphere_normals[0][0][0],sphere_normals[0][0][1],
                        sphere_normals[0][0][2],*color]))

        new_vl = np.stack(triangle_list)

        
        vl = np.array([
            # back face
            -radius/2, -radius/2, -radius/2, 0, 0, -1, *color,
            -radius/2, radius/2, -radius/2, 0, 0, -1, *color,
            radius/2, radius/2, -radius/2, 0, 0, -1, *color,            
        ]).reshape((3, 9))

        self.vertices = np.zeros([len(new_vl), 11])
        self.vertices[0:len(new_vl), 0:9] = new_vl
        # print(len(self.vertices))


        self.indices = np.zeros(0)

    def draw(self):
        self.vao.bind()
        # TODO 1.1 is at here, switch from vbo to ebo
        self.vbo.draw()
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

