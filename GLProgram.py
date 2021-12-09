from Light import Light

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
import numpy as np
import math


def perspectiveMatrix(angleOfView, near, far):
    result = np.identity(4)
    angleOfView = min(179, max(0, angleOfView))
    scale = 1 / math.tan(0.5 * angleOfView * math.pi / 180)
    fsn = far - near
    result[0, 0] = scale
    result[1, 1] = scale
    result[2, 2] = - far / fsn
    result[3, 2] = - far * near / fsn
    result[2, 3] = -1
    result[3, 3] = 0


class GLProgram:
    program = None

    vertexShaderSource = None
    fragmentShaderSource = None
    attribs = None

    vs = None  # vertex shader
    fs = None  # Fragment shader

    ready = False  # a control flag which reflect if this GLprogram is ready
    debug = 0

    def __init__(self) -> None:
        self.program = gl.glCreateProgram()

        self.ready = False

        # define attribs name and corresponding method to set it
        self.attribs = {
            "vertexPos": "aPos",
            "vertexNormal": "aNormal",
            "vertexColor": "aColor",
            "vertexTexture": "aTexture",

            "textureImage": "theTexture01",

            "projectionMat": "projection",
            "viewMat": "view",
            "modelMat": "model",

            "viewPosition": "viewPosition",
            "material": "material",
            "light": "light",

            "maxLightsNum": "20",
            "maxMaterialNum": "20",

            "specularOn": "specularOn",
            "diffuseOn": "diffuseOn",
            "ambientOn": "ambientOn"

        }
        self.attribs["diffuse"] = self.attribs["material"] + ".diffuse"
        self.attribs["specular"] = self.attribs["material"] + ".specular"
        self.attribs["ambient"] = self.attribs["material"] + ".ambient"
        self.attribs["highlight"] = self.attribs["material"] + ".highlight"

        for i in range(int(self.attribs["maxLightsNum"])):
            self.attribs[f"light[{i}].position"] = f"{self.attribs['light']}[{i}].position"
            self.attribs[f"light[{i}].color"] = f"{self.attribs['light']}[{i}].color"
            self.attribs[f"light[{i}].infiniteOn"] = f"{self.attribs['light']}[{i}].infiniteOn"
            self.attribs[f"light[{i}].infiniteDirection"] = f"{self.attribs['light']}[{i}].infiniteDirection"
            self.attribs[f"light[{i}].radialOn"] = f"{self.attribs['light']}[{i}].radialOn"
            self.attribs[f"light[{i}].spotRadialFactor"] = f"{self.attribs['light']}[{i}].spotRadialFactor"
            self.attribs[f"light[{i}].spotOn"] = f"{self.attribs['light']}[{i}].spotOn"
            self.attribs[f"light[{i}].spotDirection"] = f"{self.attribs['light']}[{i}].spotDirection"
            self.attribs[f"light[{i}].spotAngleLimit"] = f"{self.attribs['light']}[{i}].spotAngleLimit"
            self.attribs[f"light[{i}].a_L"] = f"{self.attribs['light']}[{i}].a_L"

            self.attribs[f"light[{i}].isOn"] = f"{self.attribs['light']}[{i}].isOn"


        self.vertexShaderSource = self.genVertexShaderSource()
        self.fragmentShaderSource = self.genFragShaderSource()

    def __del__(self) -> None:
        try:
            gl.glDeleteProgram(self.program)
        except Exception as e:
            pass

    @staticmethod
    def load_shader(src: str, shader_type: int) -> int:
        shader = gl.glCreateShader(shader_type)
        gl.glShaderSource(shader, src)
        gl.glCompileShader(shader)
        error = gl.glGetShaderiv(shader, gl.GL_COMPILE_STATUS)
        if error != gl.GL_TRUE:
            info = gl.glGetShaderInfoLog(shader)
            gl.glDeleteShader(shader)
            raise Exception(info)
        return shader

    def genVertexShaderSource(self):
        vss = f'''
        #version 330 core
        in vec3 {self.attribs["vertexPos"]};
        in vec3 {self.attribs["vertexNormal"]};
        in vec3 {self.attribs["vertexColor"]};
        in vec2 {self.attribs["vertexTexture"]};
        
        out vec3 vPos;
        out vec3 vColor;
        smooth out vec3 vNormal;
        out vec2 vTexture;
        out int materialIndex;
                
        uniform mat4 {self.attribs["projectionMat"]};
        uniform mat4 {self.attribs["viewMat"]};
        uniform mat4 {self.attribs["modelMat"]};
        
        void main()
        {{
            gl_Position = {self.attribs["projectionMat"]} * {self.attribs["viewMat"]} * {self.attribs["modelMat"]} * vec4({self.attribs["vertexPos"]}, 1.0);
            vPos = vec3(model * vec4({self.attribs["vertexPos"]}, 1.0));
            vColor = {self.attribs["vertexColor"]};
            vNormal = normalize(transpose(inverse({self.attribs["modelMat"]})) * vec4({self.attribs["vertexNormal"]}, 0.0) ).xyz;
            vTexture = {self.attribs["vertexTexture"]};
            
        }}
        '''
        return vss

    def genFragShaderSource(self):
        fss = f"""
        #version 330 core
        #define MAX_LIGHT_NUM {self.attribs["maxLightsNum"]}
        #define MAX_MATERIAL_NUM {self.attribs["maxMaterialNum"]}
        struct Material{{
            vec4 ambient;
            vec4 diffuse;
            vec4 specular;
            float highlight;
        }};
        
        struct Light{{
            vec3 position;
            vec4 color;
            
            bool infiniteOn;
            vec3 infiniteDirection;
            
            bool spotOn;
            vec3 spotDirection;
            vec3 spotRadialFactor;
            float spotAngleLimit;
            
            // (for angular attenuation)
            float a_L;
            bool isOn;
        }};
        
        in vec3 vPos;
        in vec3 vColor;
        smooth in vec3 vNormal;
        in vec2 vTexture;
        
        uniform int renderingFlag;
        uniform sampler2D {self.attribs["textureImage"]};
        
        uniform vec3 {self.attribs["viewPosition"]};
        uniform Material {self.attribs["material"]};
        uniform Light {self.attribs["light"]}[MAX_LIGHT_NUM];
        
        uniform bool {self.attribs["specularOn"]};
        uniform bool {self.attribs["diffuseOn"]};
        uniform bool {self.attribs["ambientOn"]};
                
        out vec4 FragColor;
        
        void main()
        {{
            // These three lines are meaningless, they only works as attributes placeholder! 
            // Otherwise glsl will optimize out our attributes
            vec4 placeHolder = vec4(vPos+vColor+vNormal+vec3(vTexture, 1), 0);
            FragColor = -1 * abs(placeHolder);
            FragColor = clamp(FragColor, 0, 1);
            
            vec4 results[8];
            for(int i=0; i<8; i+=1)
                results[i]=vec4(0.0);
            int ri=0;
            
            ////////// BONUS 7: Normal Mapping
            // Requirements:
            //   1. Perform the same steps as Texture Mapping above, except that instead of using the image for vertex 
            //   color, the image is used to modify the normals.
            //   2. Use the input normal map (“./as/normalmap.jpg”) on both the sphere and the torus.

            
            ////////// TODO 3: Illuminate your meshes
            // Requirements:
            //   Use the illumination equations we learned in the lecture to implement components for Diffuse, 
            //   Specular, and Ambient. You’ll implement the missing part in the Fragment shader source code. 
            //   This part will be implemented in OpenGL Shading Language. Your code should iterate through 
            //   all lights in the Light array.
            // Reserved for illumination rendering, routing name is "lighting" or "illumination"
            if ((renderingFlag >> 0 & 0x1) == 1){{
                vec4 result = vec4(vColor, 1.0);
                float mag_lv;
                
                // From lab: (Rendering Lights)
                for (int i = 0; i < MAX_LIGHT_NUM; i++){{  // equivalent to single bracket   
                    if ({self.attribs["light"]}[i].isOn){{    
                        float rad_atten;
                        float ang_atten;             
                        vec3 light_vector;
                        if ({self.attribs["light"]}[i].infiniteOn){{
                            light_vector = {self.attribs["light"]}[i].infiniteDirection;
                            ang_atten = 1;
                            rad_atten = 1;
                            mag_lv = sqrt(light_vector[0] * light_vector[0] + light_vector[1] * light_vector[1] + light_vector[2] * light_vector[2]);
                        }}
                        else{{
                            light_vector = {self.attribs["light"]}[i].position - vPos;  // Light to vertex
                            mag_lv = sqrt(light_vector[0] * light_vector[0] + light_vector[1] * light_vector[1] + light_vector[2] * light_vector[2]);
                            light_vector /= mag_lv;
                        }}
                        
                        // Spot Attenuation                  
                        if (!{self.attribs["light"]}[i].infiniteOn && {self.attribs["light"]}[i].spotOn){{
                            // radial atten
                            vec3 rad_factor = {self.attribs["light"]}[i].spotRadialFactor;
                            rad_atten = 1/(rad_factor[0] + rad_factor[1] * mag_lv + rad_factor[2] * mag_lv * mag_lv);
                            
                            // angular atten
                            float cos_alpha = dot(light_vector, -1*{self.attribs["light"]}[i].spotDirection);// - {self.attribs["light"]}[i].position);
                            float cos_limit = cos({self.attribs["light"]}[i].spotAngleLimit);
                            bool inCone = (cos_alpha >= cos_limit);// && (cos_alpha >= -cos_limit) ;
                            if (inCone){{
                                //ang_atten = cos_alpha;
                                ang_atten = pow(cos_alpha, {self.attribs["light"]}[i].a_L);
                            }}
                            else{{
                                ang_atten = 0;
                            }}  
                        }}
                        else{{
                            ang_atten = 1;
                            rad_atten = 1;
                        }}
                    
                
                        // Begin material lighting
                    
                        //                                             .coefficient
                        vec4 ambient_light = {self.attribs["material"]}.ambient * {self.attribs["light"]}[i].color;
                        float mag_vNormal = sqrt(vNormal[0] * vNormal[0] + vNormal[1] * vNormal[1] + vNormal[2] * vNormal[2]);
                        
                        float light_dot_n  = dot(light_vector, normalize(vNormal)); // Skips light that points away from camera
                        
                        vec4 diffuse_light;
                        if (light_dot_n > 0){{
                            diffuse_light = {self.attribs["material"]}.diffuse * {self.attribs["light"]}[i].color * light_dot_n;
                        }}
                        else{{
                            diffuse_light = vec4(0,0,0,1);
                        }}
                        
                        
                        // Specular lighting:
                        vec3 reflection = 2 * light_dot_n * vNormal - light_vector;
                        float mag_reflection = sqrt(reflection[0] * reflection[0] + reflection[1] * reflection[1] + reflection[2] * reflection[2]);
                        reflection /= mag_reflection;             
                        vec3 viewVector = {self.attribs["viewPosition"]} - vPos;
                        float mag_viewVector = sqrt(viewVector[0] * viewVector[0] + viewVector[1] * viewVector[1] + viewVector[2] * viewVector[2]);
                        viewVector /= mag_viewVector;
                        
                        float view_dot_reflect =dot(viewVector, reflection);
                        
                        vec4 specular_light;
                        if (light_dot_n > 0 && view_dot_reflect > 0){{
                            specular_light = {self.attribs["material"]}.specular * {self.attribs["light"]}[i].color * 
                                        pow(view_dot_reflect, {self.attribs["material"]}.highlight);
                        }}
                        else{{
                            specular_light = vec4(0,0,0,1);
                        }}
                        
                        if (!{self.attribs["specularOn"]}){{
                            specular_light = vec4(0,0,0,0);
                        }}
                        if (!{self.attribs["diffuseOn"]}){{
                            diffuse_light = vec4(0,0,0,0);
                        }}
                        if (!{self.attribs["ambientOn"]}){{
                            ambient_light = vec4(0,0,0, 0);
                        }}
                        
    
                        // Clamp intensity
                        //result[0] += min(1, ambient_light[0] + rad_atten * ang_atten * ( diffuse_light[0] + specular_light[0]));
                        //result[1] += min(1, ambient_light[1] + rad_atten * ang_atten * ( diffuse_light[1] + specular_light[1]));
                        //result[2] += min(1, ambient_light[2] + rad_atten * ang_atten * (  diffuse_light[2] + specular_light[2]));
                        //result[3] += min(1, ambient_light[3] + rad_atten * ang_atten * (  diffuse_light[3] + specular_light[3]));
                        result += min(vec4 (1, 1, 1, 1), ambient_light + rad_atten * ang_atten * (  diffuse_light + specular_light));
                    }} // if light is on
                }}
                
                //for light in lights: // Python implementation of above
                //    ambient_light = ka*ia
                //    result += ambient_light



                
                ////////// TODO 4: Set up lights
                // Requirements:
                //   * Use the Light struct which is defined above and the provided Light class to implement 
                //   illumination equations for 3 different light sources: Point light, Infinite light, 
                //   Spotlight with radial and angular attenuation
                //   * In the Sketch.py file Interrupt_keyboard method, bind keyboard interfaces that allows 
                //   the user to toggle on/off specular, diffuse, and ambient with keys S, D, A.
                                  
                //vec4 ambient_light = {self.attribs["material"]}.ambient ;
                //result += ambient_light;
                results[ri] = result;
                ri+=1;
            }}
            
            // Reserved for rendering with vertex color, routing name is "vertex"
            if ((renderingFlag >> 1 & 0x1) == 1){{
                results[ri] = vec4(vColor, 1.0);
                ri+=1;
            }}
            
            // Reserved for rendering with fixed color, routing name is "pure"
            if ((renderingFlag >> 2 & 0x1) == 1){{
                results[ri] = vec4(0.5, 0.5, 0.5, 1.0);
                ri+=1;
            }}
            
            // Reserved for normal rendering, routing name is "normal"
            if ((renderingFlag >> 3 & 0x1) == 1){{
            
                ////////// TODO 2: Set Normal Rendering
                // Requirements:
                //   As a visual debugging mode, you’ll implement a rendering mode that visualizes the vertex normals 
                //   with color information. In Fragment Shader, use the vertex normal as the vertex color 
                //   (i.e. the rgb values come from the xyz components of the normal). The value for each dimension in 
                //   vertex normal will be in the range -1 to 1. You will need to offset and rescale them to the 
                //   range 0 to 1.
                
                //results[ri] = vec4(abs(vNormal[0]), abs(vNormal[1]), abs(vNormal[2]), 1.0);
                
                results[ri][0] = (vNormal[0] + 1.0) / 2.0;
                results[ri][1] = (vNormal[1] + 1.0) / 2.0;
                results[ri][2] = (vNormal[2] + 1.0) / 2.0;
                results[ri][3] = 1.0;
                ri+=1;
                

                
            }}
            
            // Reserved for artist rendering, routing name is "artist"
            if ((renderingFlag >> 5 & 0x1) == 1){{
            
                ////////// BONUS 8: Artist Rendering (advanced)
                // Requirements:
                //   Look at Section 10.3, “Artistic Shading” in Shirley/Marschner (4th ed.).
                //        Implement line drawing in shader code
                //        Implement cool-to-warm shader code

                results[ri] = vec4(0.5, 0.5, 0.5, 1.0);
                ri+=1;
            }}
            
            // Reserved for some customized rendering, routing name is "custom"
            if ((renderingFlag >> 6 & 0x1) == 1){{
                results[ri] = vec4(0.5, 0.5, 0.5, 1.0);
                ri+=1;
            }}
            
            // Reserved for texture mapping, get point color from texture image and texture coordinates
            // Routing name is "texture"
            if ((renderingFlag >> 8 & 0x1) == 1){{
                results[ri] = texture({self.attribs["textureImage"]}, vTexture);
                ri+=1;
            }}
            
            // Mix all result in results array
            vec4 outputResult=vec4(0.0);
            for(int i=0; i<ri; i++){{
                outputResult += results[i]/ri;
            }}
            FragColor = outputResult;
        }}
        """
        return fss

    def set_vss(self, vss: str):
        if not isinstance(vss, str):
            raise TypeError("Vertex shader source code must be a string")
        self.vertexShaderSource = vss

    def set_fss(self, fss):
        if not isinstance(fss, str):
            raise TypeError("Fragment shader source code must be a string")
        self.fragmentShaderSource = fss

    def getAttribLocation(self, name):
        programName = self.getAttribName(name)
        attribLoc = gl.glGetAttribLocation(self.program, programName)
        if attribLoc == -1 and self.debug > 1:
            print(f"Warning: Attrib {name} cannot found. Might have been optimized off")
        return attribLoc

    def getUniformLocation(self, name, lookThroughAttribs=True):
        if lookThroughAttribs:
            variableName = self.getAttribName(name)
        else:
            variableName = name
        uniformLoc = gl.glGetUniformLocation(self.program, variableName)
        if uniformLoc == -1 and self.debug > 1:
            print(f"Warning: Uniform {name} cannot found. Might have been optimized off")
        return uniformLoc

    def getAttribName(self, attribIndexName):
        return self.attribs[attribIndexName]

    def compile(self, vs_src=None, fs_src=None) -> None:
        if vs_src:
            self.set_vss(vs_src)
        else:
            vs_src = self.vertexShaderSource

        if fs_src:
            self.set_fss(fs_src)
        else:
            fs_src = self.fragmentShaderSource

        if not (vs_src and fs_src):
            raise Exception("shader source code missing")

        vs = self.load_shader(vs_src, gl.GL_VERTEX_SHADER)
        if not vs:
            return
        fs = self.load_shader(fs_src, gl.GL_FRAGMENT_SHADER)
        if not fs:
            return
        gl.glAttachShader(self.program, vs)
        gl.glAttachShader(self.program, fs)
        gl.glLinkProgram(self.program)
        error = gl.glGetProgramiv(self.program, gl.GL_LINK_STATUS)
        if error != gl.GL_TRUE:
            info = gl.glGetShaderInfoLog(self.program)
            raise Exception(info)

        self.ready = True

    def setFragmentShaderRouting(self, routing="lighting"):
        """
        There will be different rendering routing,
        "lighting"/"illumination": DEFAULT routing. Rendering the scene with lights
        "vertex": use VBO stored vertex color to render object
        "pure": render object with pre-defined color
        "normal": render with vertex's normal
        "bump": normal mapping
        "artist": artist rendering
        "custom": some customized rendering
        "texture": this must use previous routing, if set to true, then mix color with texture
        """
        renderingFlag = 0
        if isinstance(routing, str):
            routing = routing.lower()
            if ("lighting" in routing) or ("illumination" in routing):
                renderingFlag = renderingFlag | 0x1
            if "vertex" in routing:
                renderingFlag = renderingFlag | (0x1 << 1)
            if "pure" in routing:
                renderingFlag = renderingFlag | (0x1 << 2)
            if "normal" in routing:
                renderingFlag = renderingFlag | (0x1 << 3)
            if "bump" in routing:
                renderingFlag = renderingFlag | (0x1 << 4)
            if "artist" in routing:
                renderingFlag = renderingFlag | (0x1 << 5)
            if "custom" in routing:
                renderingFlag = renderingFlag | (0x1 << 6)
            if "texture" in routing:
                renderingFlag = renderingFlag | (0x1 << 8)

        self.use()
        self.setInt("renderingFlag", renderingFlag, lookThroughAttribs=False)

    def use(self):
        """
        This is required before the uniforms set up.
        """
        if not self.ready:
            raise Exception("GLProgram must compile before use it")
        gl.glUseProgram(self.program)

    def setLight(self, lightIndex: int, light: Light):  # TODO float
        if not isinstance(light, Light):
            raise TypeError("light type must be Light")

        self.setVec3(f"""{self.attribs["light"]}[{lightIndex}].position""", light.position, False)
        self.setVec4(f"""{self.attribs["light"]}[{lightIndex}].color""", light.color, False)

        # scene 2 rendering
        self.setBool(f"""{self.attribs["light"]}[{lightIndex}].spotOn""", light.spotOn, False)
        self.setVec3(f"""{self.attribs["light"]}[{lightIndex}].spotDirection""", light.spotDirection, False)
        self.setVec3(f"""{self.attribs["light"]}[{lightIndex}].spotRadialFactor""", light.spotRadialFactor, False)
        self.setFloat(f"""{self.attribs["light"]}[{lightIndex}].spotAngleLimit""", light.spotAngleLimit, False)
        self.setFloat(f"""{self.attribs["light"]}[{lightIndex}].a_L""", light.a_L, False)

        self.setBool(f"""{self.attribs["light"]}[{lightIndex}].isOn""", light.isOn, False)

    def clearAllLights(self):
        maxLightsNum = int(self.attribs["maxLightsNum"])
        light = Light()
        for i in range(maxLightsNum):
            self.setLight(i, light)

    def setSpecular(self, bool_val):
        self.setBool(self.attribs["specularOn"], bool_val)

    def setDiffuse(self, bool_val):
        self.setBool(self.attribs["diffuseOn"], bool_val)

    def setAmbient(self, bool_val):
        self.setBool(self.attribs["ambientOn"], bool_val)

    # some help methods to set uniform in program
    def setMat4(self, name, mat, lookThroughAttribs=True):
        self.use()
        if mat.shape != (4, 4):
            raise Exception("Projection Matrix must have 4x4 shape")
        gl.glUniformMatrix4fv(self.getUniformLocation(name, lookThroughAttribs), 1, gl.GL_FALSE, mat.flatten("C"))

    def setMat3(self, name, mat, lookThroughAttribs=True):
        self.use()
        if mat.shape != (3, 3):
            raise Exception("Projection Matrix must have 3x3 shape")
        gl.glUniformMatrix3fv(self.getUniformLocation(name, lookThroughAttribs), 1, gl.GL_FALSE, mat.flatten("C"))

    def setMat2(self, name, mat, lookThroughAttribs=True):
        self.use()
        if mat.shape != (2, 2):
            raise Exception("Projection Matrix must have 2x2 shape")
        gl.glUniformMatrix2fv(self.getUniformLocation(name, lookThroughAttribs), 1, gl.GL_FALSE, mat.flatten("C"))

    def setVec4(self, name, vec, lookThroughAttribs=True):
        self.use()
        if vec.size != 4:
            raise Exception("Vector must have size 4")
        gl.glUniform4fv(self.getUniformLocation(name, lookThroughAttribs), 1, vec)

    def setVec3(self, name, vec, lookThroughAttribs=True):
        self.use()
        if vec.size != 3:
            raise Exception("Vector must have size 3")
        gl.glUniform3fv(self.getUniformLocation(name, lookThroughAttribs), 1, vec)

    def setVec2(self, name, vec, lookThroughAttribs=True):
        self.use()
        if vec.size != 2:
            raise Exception("Vector must have size 2")
        gl.glUniform2fv(self.getUniformLocation(name, lookThroughAttribs), 1, vec)

    def setBool(self, name, value, lookThroughAttribs=True):
        self.use()
        if value not in (0, 1):
            raise Exception("bool only accept True/False/0/1")
        gl.glUniform1i(self.getUniformLocation(name, lookThroughAttribs), int(value))

    def setInt(self, name, value, lookThroughAttribs=True):
        self.use()
        if value != int(value):
            raise Exception("set int only accept  integer")
        gl.glUniform1i(self.getUniformLocation(name, lookThroughAttribs), int(value))

    def setFloat(self, name, value, lookThroughAttribs=True):
        self.use()
        gl.glUniform1f(self.getUniformLocation(name, lookThroughAttribs), float(value))


