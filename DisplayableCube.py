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


class DisplayableCube(Displayable):
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

    def __init__(self, shaderProg, length=1, width=1, height=1, color=ColorType.BLUE):
        super(DisplayableCube, self).__init__()
        self.shaderProg = shaderProg
        self.shaderProg.use()

        self.vao = VAO()
        self.vbo = VBO()  # vbo can only be initiate with glProgram activated
        self.ebo = EBO()

        self.generate(length, width, height, color)

    def generate(self, length=1, width=1, height=1, color=None):
        self.length = length
        self.width = width
        self.height = height
        self.color = color

        '''
        self.vertices = np.zeros([36, 11])
        vl = np.array([
            # back face
            -length/2, -width/2, -height/2, 0, 0, -1, *color,   # vert0
            -length/2, width/2, -height/2, 0, 0, -1, *color,    # vert1
            length/2, width/2, -height/2, 0, 0, -1, *color,     # vert3
            -length/2, -width/2, -height/2, 0, 0, -1, *color,   # vert0
            length/2, width/2, -height/2, 0, 0, -1, *color,     # vert3
            length/2, -width/2, -height/2, 0, 0, -1, *color,    # vert4
            # front face
            -length/2, -width/2, height/2, 0, 0, 1, *color,     # vert5
            length/2, -width/2, height/2, 0, 0, 1, *color,      # vert6
            length/2, width/2, height/2, 0, 0, 1, *color,       # vert7
            -length/2, -width/2, height/2, 0, 0, 1, *color,     # vert5
            length/2, width/2, height/2, 0, 0, 1, *color,       # vert7
            -length/2, width/2, height/2, 0, 0, 1, *color,      # vert8
            # left face
            -length/2, -width/2, -height/2, -1, 0, 0, *color,   # vert0
            -length/2, -width/2, height/2, -1, 0, 0, *color,    # vert5
            -length/2, width/2, height/2, -1, 0, 0, *color,     # vert8
            -length/2, -width/2, -height/2, -1, 0, 0, *color,   # vert0
            -length/2, width/2, height/2, -1, 0, 0, *color,     # vert8
            -length/2, width/2, -height/2, -1, 0, 0, *color,    # vert1
            # right face
            length/2, -width/2, height/2, 1, 0, 0, *color,      # vert6
            length/2, -width/2, -height/2, 1, 0, 0, *color,     # vert4
            length/2, width/2, -height/2, 1, 0, 0, *color,      # vert3
            length/2, -width/2, height/2, 1, 0, 0, *color,      # vert6
            length/2, width/2, -height/2, 1, 0, 0, *color,      # vert3
            length/2, width/2, height/2, 1, 0, 0, *color,       # vert7
            # top face
            -length/2, width/2, height/2, 0, 1, 0, *color,      # vert8
            length/2, width/2, height/2, 0, 1, 0, *color,       # vert7
            length/2, width/2, -height/2, 0, 1, 0, *color,      # vert3
            -length/2, width/2, height/2, 0, 1, 0, *color,      # vert8
            length/2, width/2, -height/2, 0, 1, 0, *color,      # vert3
            -length/2, width/2, -height/2, 0, 1, 0, *color,     # vert1
            # bot face
            -length/2, -width/2, -height/2, 0, -1, 0, *color,   # vert0
            length/2, -width/2, -height/2, 0, -1, 0, *color,    # vert4
            length/2, -width/2, height/2, 0, -1, 0, *color,     # vert6
            -length/2, -width/2, -height/2, 0, -1, 0, *color,   # vert0
            length/2, -width/2, height/2, 0, -1, 0, *color,     # vert6
            -length/2, -width/2, height/2, 0, -1, 0, *color,    # vert5
        ]).reshape((36, 9))
        self.vertices[0:36, 0:9] = vl
        
        self.indices = np.zeros(0)
        '''


        self.vertices = np.zeros([24, 11])
        vl = np.array([
            # back face - 0, 1, 2, 0, 2, 3
            -length / 2, -width / 2, -height / 2, 0, 0, -1, *color,  # vert0
            -length / 2, width / 2, -height / 2, 0, 0, -1, *color,  # vert1
            length / 2, width / 2, -height / 2, 0, 0, -1, *color,  # vert2
            length / 2, -width / 2, -height / 2, 0, 0, -1, *color,  # vert3
            # front face - 4, 5, 6, 4, 6, 7
            -length / 2, -width / 2, height / 2, 0, 0, 1, *color,  # vert4
            length / 2, -width / 2, height / 2, 0, 0, 1, *color,  # vert5
            length / 2, width / 2, height / 2, 0, 0, 1, *color,  # vert6
            -length / 2, width / 2, height / 2, 0, 0, 1, *color,  # vert7
            # left face - 8, 9, 10, 8, 10, 11
            -length / 2, -width / 2, -height / 2, -1, 0, 0, *color,  # vert8
            -length / 2, -width / 2, height / 2, -1, 0, 0, *color,  # vert9
            -length / 2, width / 2, height / 2, -1, 0, 0, *color,  # vert10
            -length / 2, width / 2, -height / 2, -1, 0, 0, *color,  # vert11
            # right face - 12, 13, 14, 12, 14, 15
            length / 2, -width / 2, height / 2, 1, 0, 0, *color,  # vert12
            length / 2, -width / 2, -height / 2, 1, 0, 0, *color,  # vert13
            length / 2, width / 2, -height / 2, 1, 0, 0, *color,  # vert14
            length / 2, width / 2, height / 2, 1, 0, 0, *color,  # vert715
            # top face - 16, 17, 18, 16, 18, 19
            -length / 2, width / 2, height / 2, 0, 1, 0, *color,  # vert16
            length / 2, width / 2, height / 2, 0, 1, 0, *color,  # vert17
            length / 2, width / 2, -height / 2, 0, 1, 0, *color,  # vert18
            -length / 2, width / 2, -height / 2, 0, 1, 0, *color,  # vert19
            # bot face - 20, 21, 22, 20, 22, 23
            -length / 2, -width / 2, -height / 2, 0, -1, 0, *color,  # vert20
            length / 2, -width / 2, -height / 2, 0, -1, 0, *color,  # vert21
            length / 2, -width / 2, height / 2, 0, -1, 0, *color,  # vert22
            -length / 2, -width / 2, height / 2, 0, -1, 0, *color,  # vert23
        ]).reshape((24, 9))
        self.indices = np.array([
            0, 1, 2, 0, 2, 3,
            4, 5, 6, 4, 6, 7,
            8, 9, 10, 8, 10, 11,
            12, 13, 14, 12, 14, 15,
            16, 17, 18, 16, 18, 19,
            20, 21, 22, 20, 22, 23
        ])
        self.vertices[0:24, 0:9] = vl



    def draw(self):
        self.vao.bind()
        # TODO 1.1 is at here, switch from vbo to ebo
        # self.vbo.draw()
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

