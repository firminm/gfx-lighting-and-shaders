"""
Define Torus here.
First version in 11/01/2021

:author: micou(Zezhou Sun)
:version: 2021.1.1
"""

from Displayable import Displayable
from GLBuffer import VAO, VBO, EBO
from Point import Point
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

##### TODO 6/BONUS 6: Texture Mapping
# Requirements:
#   1. Set up each object's vertex texture coordinates(2D) to the self.vertices 9:11 columns
#   (i.e. the last two columns). Tell OpenGL how to interpret these two columns:
#   you need to set up attribPointer in the Displayable object's initialize method.
#   2. Generate texture coordinates for the torus and sphere. Use “./assets/marble.jpg” for the torus and
#   “./assets/earth.jpg” for the sphere as the texture image.
#   There should be no seams in the resulting texture-mapped model.

class DisplayableTorus(Displayable):
    vao = None
    vbo = None
    ebo = None
    shaderProg = None

    # stores current torus's information, read-only
    nsides = 0
    rings = 0
    innerRadius = 0
    outerRadius = 0
    color = None

    vertices = None
    indices = None

    def __init__(self, shaderProg, innerRadius=0.25, outerRadius=0.5, nsides=36, rings=36, color=ColorType.SOFTBLUE):
        super(DisplayableTorus, self).__init__()
        self.shaderProg = shaderProg
        self.shaderProg.use()

        self.vao = VAO()
        self.vbo = VBO()  # vbo can only be initiate with glProgram activated
        self.ebo = EBO()

        self.generate(innerRadius, outerRadius, nsides, rings, color)

    def generate(self, innerRadius=0.25, outerRadius=0.5, nsides=36, rings=36, color=ColorType.SOFTBLUE):
        self.innerRadius = innerRadius
        self.outerRadius = outerRadius
        self.nsides = nsides
        self.rings = rings
        self.color = color
        pi = math.pi

        r = (outerRadius - innerRadius) / 2
        raxial = innerRadius + r

        num_divisions = (rings) * (nsides-1)

        torus_vertices = np.zeros([nsides + 1, rings + 1, 3])
        torus_normals  = np.zeros([nsides + 1, rings + 1, 3])

        for i, phi in enumerate(np.arange(-pi, pi + 2 * pi / nsides, 2 * pi / nsides)):
            for j, theta in enumerate(np.arange(-pi, pi + 2 * pi / rings, 2 * pi / rings)):

                x = (raxial + r * math.cos(theta)) * math.cos(phi)
                y = (raxial + r * math.cos(theta)) * math.sin(phi)
                z = r * math.sin(theta)

                x_normal = math.cos(phi) * math.cos(theta)
                y_normal = math.sin(phi) * math.cos(theta)
                z_normal = math.sin(theta)

                torus_vertices[i][j] = [x, y, z]
                torus_normals[i][j] = [x_normal, y_normal, z_normal]


        indices = []
        cidx = 0

        triangle_list = []
        for i in range(nsides + 1):
            for j in range(rings + 1):
                triangle_list.append(np.array([
                        torus_vertices[i][j][0], torus_vertices[i][j][1], torus_vertices[i][j][2],
                        torus_normals[i][j][0], torus_normals[i][j][1], torus_normals[i][j][2], *color
                ]))

                if i < nsides and j < rings:
                    indices.extend([
                        cidx, cidx + 1, cidx + 1 + rings,
                        cidx, cidx + rings, cidx + 1 + rings
                    ])

                elif i == nsides and j < rings:
                    # connect back to first ring
                    indices.extend([
                        cidx, cidx + 1, j + 1,
                        cidx, j, j + 1
                    ])

                elif i < nsides and j == rings:
                    indices.extend([
                        cidx, cidx - j, cidx - (rings - j) + 1,
                        cidx, cidx + rings, cidx - rings + j + 1
                    ])
                elif i == nsides and j == rings:
                    indices.extend([
                        cidx, cidx - j, 0,
                        cidx, j, 0
                    ])
                cidx += 1

        new_vl = np.stack(triangle_list)
        # from ellipsoid
        self.vertices = np.zeros([len(new_vl), 11])
        self.vertices[0:len(new_vl), 0:9] = new_vl


        self.indices = np.asarray(indices)

        '''  Default in skeleton
        # we need to pad one more row for both nsides and rings, to assign correct texture coord to them
        self.vertices = np.zeros([(nsides) * (rings), 11])

        self.indices = np.zeros(0)
        '''

    def draw(self):
        self.vao.bind()
        self.ebo.draw()
        self.vao.unbind()

    def initialize(self):
        """
        Remember to bind VAO before this initialization. If VAO is not bind, program might throw an error
        in systems which don't enable a default VAO after GLProgram compilation
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

        self.vao.unbind()
