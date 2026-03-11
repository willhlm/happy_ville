from importlib import resources
import warnings
import numbers
from math import sin, cos
import math
import re

import moderngl
from moderngl import Texture, Context, NEAREST
import numpy as np
from OpenGL.GL import glGetUniformBlockIndex, glUniformBlockBinding
import pygame

from pygame_render.font_atlas import FontAtlas
from pygame_render.layer import Layer
from pygame_render.shader import Shader
from pygame_render.util import (
    normalize_color_arguments,
    create_rotated_rect,
    to_dest_coords,
    to_source_coords,
)


class RenderEngine:
    """
    A rendering engine for 2D graphics using Pygame and ModernGL.

    This class initializes a rendering environment, including setting up Pygame for window creation,
    configuring OpenGL with ModernGL, and loading shaders for drawing. It provides a simple interface
    for creating and managing rendering layers, as well as drawing operations using shaders.
    """
    _DEFAULT_INSTANCED_ATTRS = (("position", 2), ("scale", 2), ("angle", 1))
    # Reserved / engine-owned names that must not be used as instance attribute names.
    _RESERVED_INSTANCE_ATTR_NAMES = {
        "vertexPos",
        "vertexTexCoord",
        "fragmentTexCoord",
        "position",
        "scale",
        "angle",
                "screenSize",
        "gl_Position",
    }

    def _validate_instance_attribute_name(self, name: str) -> None:
        # Prevent collisions with engine-defined symbols and varyings.
        if name in self._RESERVED_INSTANCE_ATTR_NAMES:
            raise ValueError(
                f"Instance attribute name '{name}' is reserved by the engine."
            )
        if name.startswith("v_"):
            raise ValueError(
                "Instance attribute names must not start with 'v_' (reserved for varyings)."
            )
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name):
            raise ValueError(
                f"Instance attribute name '{name}' is not a valid GLSL identifier."
            )


    def __init__(
        self,
        screen_width: int,
        screen_height: int,
        fullscreen: int | bool = 0,
        resizable: int | bool = 0,
        noframe: int | bool = 0,
        scaled: int | bool = 0,
        depth: int = 0,
        display: int = 0,
        vsync: int = 0,
    ) -> None:
        """
        Initialize a rendering engine using Pygame and ModernGL.

        Parameters:
        - screen_width (int): The width of the rendering window.
        - screen_height (int): The height of the rendering window.
        - fullscreen (int or bool, optional): Set to 1 or True to enable fullscreen mode, 0 or False to disable. Default is 0.
        - resizable (int or bool, optional): Set to 1 or True to enable window resizing, 0 or False to disable. Default is 0.
        - noframe (int or bool, optional): Set to 1 or True to remove window frame, 0 or False to keep the frame. Default is 0.
        - scaled (int or bool, optional): Set to 1 or True to enable display scaling, 0 or False to disable. Default is 0.
        - depth (int, optional): Depth of the rendering window. Default is 0.
        - display (int, optional): The display index to use. Default is 0.
        - vsync (int, optional): Set to 1 to enable vertical synchronization, 0 to disable. Default is 0.

        Raises:
        - AssertionError: If Pygame is not initialized. Call pygame.init() before using the rendering engine.

        Note: Make sure to call pygame.init() before creating an instance of RenderEngine.
        """

        # Check that pygame has been initialized
        assert (
            pygame.get_init()
        ), "Error: Pygame is not initialized. Please ensure you call pygame.init() before using the lighting engine."

        # Set OpenGL version to 3.3 core
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION, 3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION, 3)
        pygame.display.gl_set_attribute(
            pygame.GL_CONTEXT_PROFILE_MASK, pygame.GL_CONTEXT_PROFILE_CORE
        )

        # Set multi-sample buffer for MSAA
        # pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLEBUFFERS, 1)

        # Configure pygame display
        self._screen_res = (screen_width, screen_height)
        flags = pygame.OPENGL | pygame.DOUBLEBUF
        if fullscreen:
            flags |= pygame.FULLSCREEN
        if resizable:
            flags |= pygame.RESIZABLE
        if noframe:
            flags |= pygame.NOFRAME
        if scaled:
            flags |= pygame.SCALED
        pygame.display.set_mode(
            self._screen_res, flags, depth=depth, display=display, vsync=vsync
        )

        # Create an OpenGL context
        self._ctx = moderngl.create_context()

        # Configure alpha blending
        self._ctx.enable(moderngl.BLEND)
        self._ctx.blend_func = (
            moderngl.SRC_ALPHA,
            moderngl.ONE_MINUS_SRC_ALPHA,
            moderngl.ONE,
            moderngl.ONE_MINUS_SRC_ALPHA,
        )
        self._ctx.blend_equation = moderngl.FUNC_ADD

        # Create screen layer
        self._screen = Layer(None, self._ctx.screen)
        self._ctx.screen

        # Read draw shader source files
        vertex_src = resources.read_text("pygame_render", "vertex.glsl")
        fragment_src_draw = resources.read_text("pygame_render", "fragment_draw.glsl")
        self._instanced_vertex_template = resources.read_text(
            "pygame_render", "vertex_instanced_template.glsl"
        )

        # Create draw shader program
        prog_draw = self._ctx.program(
            vertex_shader=vertex_src, fragment_shader=fragment_src_draw
        )
        self._shader_draw = Shader(prog_draw)
        self._shader_draw_instanced = self.compile_shader(
            fragment_source=fragment_src_draw,
            instanced=True,
            instanced_uv_rect=True,
        )

        # Read the tone mapping shader
        fragment_src_tonemap = resources.read_text(
            "pygame_render", "fragment_tone.glsl"
        )

        # Create draw shader program
        prog_tonemap = self._ctx.program(
            vertex_shader=vertex_src, fragment_shader=fragment_src_tonemap
        )
        self._shader_tonemap = Shader(prog_tonemap)
        self._shader_tonemap_instanced = self.compile_shader(
            fragment_source=fragment_src_tonemap,
            instanced=True,
            instanced_uv_rect=True,
        )
        self._exposure: float
        self.HDR_exposure = 0.1

        # Create a shader program for drawing primitives
        self.prog_prim = self.ctx.program(
            vertex_shader="""
            #version 330
            in vec2 vert;
            void main() {
            gl_Position = vec4(vert.x, vert.y, 0.0, 1.0);
            }""",
            fragment_shader="""
            #version 330
            uniform vec4 primColor;
            out vec4 color;
            void main() {
            color = primColor;
            }""",
        )

        # Read the text shader
        fragment_src_text = resources.read_text("pygame_render", "fragment_text.glsl")

        # Create text shader program
        prog_text = self._ctx.program(
            vertex_shader=vertex_src, fragment_shader=fragment_src_text
        )
        self._shader_text = Shader(prog_text)

        # Shared resources for unique instanced rendering
        base_quad_pos = np.array(
            [
                [-0.5, -0.5],
                [0.5, -0.5],
                [-0.5, 0.5],
                [-0.5, 0.5],
                [0.5, -0.5],
                [0.5, 0.5],
            ],
            dtype=np.float32,
        )
        base_quad_uv = np.array(
            [
                [0.0, 1.0],
                [1.0, 1.0],
                [0.0, 0.0],
                [0.0, 0.0],
                [1.0, 1.0],
                [1.0, 0.0],
            ],
            dtype=np.float32,
        )
        self._instanced_base_pos_vbo = self._ctx.buffer(base_quad_pos.tobytes())
        self._instanced_base_uv_vbo = self._ctx.buffer(base_quad_uv.tobytes())
        self._instanced_vao_cache: dict[
            tuple[int, tuple[tuple[str, int], ...]], dict
        ] = {}
        self._instanced_shader_variant_cache: dict[tuple[int, tuple[tuple[str, int], ...], bool, str], Shader] = {}

        self._quad_vbo = self._ctx.buffer(reserve=24 * 4)
        self._quad_vao_cache = {}  # key: shader.program.glo -> vao   

    @property
    def screen(self) -> Layer:
        """Get the screen layer."""
        return self._screen

    @property
    def ctx(self) -> Context:
        """Get the ModernGL rendering context."""
        return self._ctx

    @property
    def display_size(self) -> tuple[int, int]:
        return pygame.display.get_window_size()

    @property
    def HDR_exposure(self) -> float:
        return self._exposure

    @HDR_exposure.setter
    def HDR_exposure(self, value: float) -> None:
        self._exposure = value
        self._shader_tonemap["exposure"] = value

    def use_alpha_blending(self, enabled: bool) -> None:
        """
        Enable or disable alpha blending.

        Args:
            enabled (bool): True to enable, False to disable premultiplied alpha blending.
        """
        if enabled:
            self._ctx.enable(moderngl.BLEND)
        else:
            self._ctx.disable(moderngl.BLEND)

    def surface_to_texture(self, sfc: pygame.Surface) -> moderngl.Texture:
        """
        Convert a pygame.Surface to a moderngl.Texture.

        Args:
            sfc (pygame.Surface): Surface to convert.

        Returns:
            moderngl.Texture: Converted texture.
        """

        img_flip = pygame.transform.flip(sfc, False, True)
        img_data = pygame.image.tostring(img_flip, "RGBA")

        tex = self._ctx.texture(sfc.get_size(), components=4, data=img_data)
        tex.filter = (moderngl.NEAREST, moderngl.NEAREST)
        return tex

    def load_texture(self, path: str) -> moderngl.Texture:
        """
        Load a texture from a file.

        Args:
            path (str): Path to the texture file.

        Returns:
            moderngl.Texture: Loaded texture.
        """

        img = pygame.image.load(path).convert_alpha()
        return self.surface_to_texture(img)

    def make_layer(
        self,
        size: tuple[int, int],
        components: int = 4,
        data: bytes | None = None,
        samples: int = 0,
        alignment: int = 1,
        dtype: str = "f1",
        internal_format: int | None = None,
    ) -> Layer:
        """
        Create a rendering layer with optional parameters. A layer consists of a texture and a framebuffer.

        Parameters:
        - size (tuple[int, int]): The dimensions (width, height) of the texture.
        - components (int): The number of components per texel (e.g., 1 for red, 3 for RGB, 4 for RGBA).
        - data (bytes | None): Optional initial data for the texture. If None, the texture data is uninitialized.
        - samples (int): The number of samples. Value 0 means no multisample format.
        - alignment (int): The byte alignment 1, 2, 4 or 8.
        - dtype (str): Data type ('f4' for HDR textures).
        - internal_format (int): Override the internal format of the texture (IF needed).

        Returns:
        - Layer
        """
        tex = self.ctx.texture(
            size,
            components,
            data,
            samples=samples,
            alignment=alignment,
            dtype=dtype,
            internal_format=internal_format,
        )
        tex.filter = (NEAREST, NEAREST)
        fbo = self.ctx.framebuffer([tex])
        return Layer(tex, fbo)

    def _generate_instanced_vertex_source(
        self,
        instance_varyings: dict[str, int] | None = None,
        vertex_hook: str = "",
        instanced_uv_rect: bool = False,
    ) -> str:
        varying_decl_in = []
        varying_decl_out = []
        varying_assign = []
        for name, components in (instance_varyings or {}).items():
            if components < 1 or components > 4:
                raise ValueError(
                    f"instance_varyings['{name}'] must have 1-4 components"
                )
            glsl_type = "float" if components == 1 else f"vec{components}"
            varying_decl_in.append(f"in {glsl_type} a_{name};")
            varying_decl_out.append(f"out {glsl_type} v_{name};")
            varying_decl_out.append(f"out {glsl_type} {name};")
            varying_assign.append(f"    v_{name} = a_{name};")
            varying_assign.append(f"    {name} = a_{name};")

        uv_decl = ""
        uv_apply = ""
        if instanced_uv_rect:
            uv_decl = "in vec2 uv_offset;\nin vec2 uv_scale;"
            uv_apply = "fragmentTexCoord = vertexTexCoord * uv_scale + uv_offset;"

        source = self._instanced_vertex_template
        source = source.replace(
            "// <AUTO_VARYINGS_ATTR_IN>", "\n".join(varying_decl_in) or ""
        )
        source = source.replace("// <AUTO_UVRECT_ATTR_IN>", uv_decl)
        source = source.replace(
            "// <AUTO_VARYINGS_OUT>", "\n".join(varying_decl_out) or ""
        )
        source = source.replace("// <AUTO_UVRECT_APPLY>", uv_apply)
        source = source.replace(
            "// <AUTO_VARYINGS_ASSIGN>", "\n".join(varying_assign) or ""
        )
        source = source.replace("// <USER_HOOK>", vertex_hook or "")
        return source

    def _infer_instance_varyings(
        self, instance_attributes: dict[str, np.ndarray] | None
    ) -> dict[str, int]:
        inferred: dict[str, int] = {}
        for name, values in (instance_attributes or {}).items():
            self._validate_instance_attribute_name(name)
            arr = np.asarray(values, dtype=np.float32)
            if arr.ndim == 1:
                arr = arr.reshape(-1, 1)
            components = int(arr.shape[1])
            if components < 1 or components > 4:
                raise ValueError(
                    f"Instance attribute '{name}' must have 1-4 components"
                )
            inferred[name] = components
        return inferred

    def _infer_instance_varyings_from_fragment_source(
        self, fragment_source: str
    ) -> dict[str, int]:
        """
        Infer instance varyings from fragment inputs named either `v_<name>`
        or `<name>`. Example: `in vec4 v_tint;` or `in vec4 tint;`.
        """
        type_to_components = {
            "float": 1,
            "vec2": 2,
            "vec3": 3,
            "vec4": 4,
        }
        inferred: dict[str, int] = {}
        pattern = re.compile(
            r"^\s*(?:layout\s*\([^)]+\)\s*)?in\s+(float|vec[2-4])\s+([A-Za-z_]\w*)\s*;",
            re.MULTILINE,
        )
        for glsl_type, raw_name in pattern.findall(fragment_source):
            if raw_name == "fragmentTexCoord":
                continue
            name = raw_name[2:] if raw_name.startswith("v_") else raw_name
            self._validate_instance_attribute_name(name)
            inferred[name] = type_to_components[glsl_type]
        return inferred

    def make_shader(
        self,
        vertex_source: str | None = None,
        fragment_source: str | None = None,
        vertex_src: str | None = None,
        fragment_src: str | None = None,
        *,
        instanced: bool = False,
        instance_varyings: dict[str, int] | None = None,
        vertex_hook: str = "",
        instanced_uv_rect: bool = False,
    ) -> Shader:
        """
        Creates a shader program using the provided vertex and fragment shader source code.

        Parameters:
        - vertex_src (str): A string containing the source code for the vertex shader.
        - fragment_src (str): A string containing the source code for the fragment shader.

        Returns:
        - A Shader object representing the compiled shader program.

        Note: If you want to load the shader source code from a file path, consider using the
        'load_shader_from_path' method instead.
        """
        if vertex_source is None and vertex_src is not None:
            vertex_source = vertex_src
        if fragment_source is None and fragment_src is not None:
            fragment_source = fragment_src

        if fragment_source is None:
            raise ValueError("fragment_source cannot be None")
        if instanced and vertex_source is None:
            vertex_source = self._generate_instanced_vertex_source(
                instance_varyings=instance_varyings,
                vertex_hook=vertex_hook,
                instanced_uv_rect=instanced_uv_rect,
            )
        if vertex_source is None:
            raise ValueError("vertex_source cannot be None when instanced is False")

        prog = self.ctx.program(
            vertex_shader=vertex_source,
            fragment_shader=fragment_source,
        )
        shader = Shader(prog)
        return shader

    def compile_shader(
        self,
        fragment_source: str | None = None,
        vertex_source: str | None = None,
        fragment_src: str | None = None,
        vertex_src: str | None = None,
        vertex_hook: str = "",
        instanced: bool = False,
        instance_varyings: dict[str, int] | None = None,
        instanced_uv_rect: bool = False,
    ) -> Shader:
        """
        Compile a shader using either a provided vertex shader or an auto-generated
        instanced vertex shader.
        """
        if fragment_source is None:
            fragment_source = fragment_src
        if vertex_source is None:
            vertex_source = vertex_src
        if fragment_source is None:
            raise ValueError("fragment_source cannot be None")
        if instanced and vertex_source is None and instance_varyings is None:
            instance_varyings = self._infer_instance_varyings_from_fragment_source(
                fragment_source
            )

        shader = self.make_shader(
            vertex_source=vertex_source,
            fragment_source=fragment_source,
            instanced=instanced,
            instance_varyings=instance_varyings,
            vertex_hook=vertex_hook,
            instanced_uv_rect=instanced_uv_rect,
        )
        if instanced and vertex_source is None:
            shader._instanced_auto_vertex = True
            shader._instanced_fragment_source = fragment_source
            shader._instanced_vertex_hook = vertex_hook
            shader._instanced_uv_rect = instanced_uv_rect
            if instance_varyings is None:
                # Enable lazy varying inference from instance_attributes in render_batch_instanced.
                shader._instanced_auto_infer_varyings = True
        return shader

    def make_font_atlas(self, font_path: str = None, font_size: int = 64) -> FontAtlas:
        return FontAtlas(self, font_path, font_size)

    def load_shader_from_path(
        self,
        vertex_path: str,
        fragment_path: str,
        *,
        instanced: bool = False,
        instance_varyings: dict[str, int] | None = None,
        vertex_hook: str = "",
        instanced_uv_rect: bool = False,
    ) -> Shader:
        """
        Loads shader source code from specified file paths and creates a shader program.

        Parameters:
        - vertex_path (str): File path to the vertex shader source code.
        - fragment_path (str): File path to the fragment shader source code.

        Returns:
        - A Shader object representing the compiled shader program.
        """
        with open(vertex_path) as f:
            vertex_src = f.read()
        with open(fragment_path) as f:
            fragment_src = f.read()

        return self.make_shader(
            vertex_source=vertex_src,
            fragment_source=fragment_src,
            instanced=instanced,
            instance_varyings=instance_varyings,
            vertex_hook=vertex_hook,
            instanced_uv_rect=instanced_uv_rect,
        )

    def load_fragment_shader_from_path(
        self,
        fragment_path: str,
        *,
        instanced: bool = True,
        vertex_source: str | None = None,
        vertex_hook: str = "",
        instance_varyings: dict[str, int] | None = None,
        instanced_uv_rect: bool = False,
    ) -> Shader:
        """
        Load a fragment shader from disk.

        By default (`instanced=True`), the engine auto-generates an instanced vertex
        shader when `vertex_source` is not provided.

        Parameters:
        - fragment_path: Path to a fragment shader source file.
        - instanced: If True, use the engine's auto-instanced vertex pipeline.
        - vertex_source: Optional custom vertex shader source. If provided, this is
          used directly instead of generating one.
        - vertex_hook: Optional raw GLSL snippet inserted into `main()` of the
          auto-generated instanced vertex shader (at `// <USER_HOOK>`).
        - instance_varyings: Optional explicit mapping of extra per-instance
          attributes to component counts, e.g. `{"tint": 4, "glow": 1}`.
          If omitted, the engine can infer from fragment `in` declarations.
        - instanced_uv_rect: If True, the generated vertex shader includes
          `uv_offset` and `uv_scale` per-instance attributes for sub-rect / atlas UVs.

        Example:
        ```python
        shader = engine.load_fragment_shader_from_path(
            "fragment_glow.glsl",
            instanced=True,
            vertex_hook=\"\"\"
                // wobble in clip space
                gl_Position.xy += vec2(0.0, sin(position.x * 0.02) * 0.01);
            \"\"\",
            instance_varyings={"tint": 4, "glow": 1},
            instanced_uv_rect=True,
        )
        ```        
        """
        with open(fragment_path) as f:
            fragment_src = f.read()
        return self.compile_shader(
            fragment_source=fragment_src,
            vertex_source=vertex_source,
            vertex_hook=vertex_hook,#raw glsl code noe can suplplycan
            instanced=instanced,
            instance_varyings=instance_varyings,#if one wants to be explicity and not rely on autmatic one in engine
            instanced_uv_rect=instanced_uv_rect,#useful for spriteet
        )

    def reserve_uniform_block(self, shader: Shader, ubo_name: str, nbytes: int) -> None:
        """
        Allocate the memory for a uniform block in a given shader.

        Parameters:
        - shader (Shader): The shader program for which the uniform block will be reserved.
        - ubo_name (str): The name of the uniform block in the shader program.
        - nbytes (int): The size, in bytes, to reserve for the uniform block in the buffer.
        """
        # Program's GL object
        prog_glo = shader.program.glo

        # Bind uniform block to given binding
        binding = shader.sample_ubo_binding()
        block_index = glGetUniformBlockIndex(prog_glo, ubo_name)
        glUniformBlockBinding(prog_glo, block_index, binding)

        # Create the uniform block
        ubo = self.ctx.buffer(reserve=nbytes)
        ubo.bind_to_uniform_block(binding)
        shader.add_ubo(ubo, ubo_name)

    def clear(self, R: int | tuple[int] = 0, G: int = 0, B: int = 0, A: int = 255):
        """
        Clear the screen with a color.

        Args:
            R (int or tuple[int]): Red component value or tuple containing RGB or RGBA values (0-255).
            G (int): Green component value (0-255).
            B (int): Blue component value (0-255).
            A (int): Alpha component value (0-255).
        """
        R, G, B, A = normalize_color_arguments(R, G, B, A)
        self._ctx.screen.clear(R, G, B, A)

    def render(
        self,
        tex: Texture,
        layer: Layer,
        position: tuple[float, float] = (0, 0),
        scale: tuple[float, float] | float = (1.0, 1.0),
        angle: float = 0.0,
        flip: tuple[bool, bool] | bool = (False, False),
        section: pygame.Rect | None = None,
        shader: Shader = None,
        hdr_render: bool = False,
    ) -> None:
        """
        Render a texture onto a layer with optional transformations.

        Parameters:
        - tex (Texture): The texture to render.
        - layer (Layer): The layer to render onto.
        - position (tuple[float, float]): The position (x, y) where the texture will be rendered. Default is (0, 0).
        - scale (tuple[float, float] | float): The scaling factor for the texture. Can be a tuple (x, y) or a scalar. Default is (1.0, 1.0).
        - angle (float): The rotation angle in degrees. Default is 0.0.
        - flip (tuple[bool, bool] | bool): Whether to flip the texture. Can be a tuple (flip x axis, flip y axis) or a boolean (flip x axis). Default is (False, False).
        - section (pygame.Rect | None): The section of the texture to render. If None, the entire texture is rendered. Default is None.
        - shader (Shader): The shader program to use for rendering. If None, a default shader is used. Default is None.
        - hdr_render (bool): Whether to render using HDR texture with tone mapping. Default is False (SDR).

        Returns:
        None

        Note:
        - If scale is a scalar, it will be applied uniformly to both x and y.
        - If flip is a boolean, it will only affect the x axis.
        - If section is None, the entire texture is used.
        - If section is larger than the texture, the texture is repeated to fill the section.
        - If shader is None, a default shader (_prog_draw) is used.
        - If hdr_render is True, it uses an HDR texture with tone mapping applied.
        """

        # Create section rect if none
        if section == None:
            section = pygame.Rect(0, 0, tex.width, tex.height)

        # If the scale is not a tuple but a scalar, convert it into a tuple
        if isinstance(scale, numbers.Number):
            scale = (scale, scale)

        # If flip is not a tuple but a boolean, convert it into a tuple
        if isinstance(flip, bool):
            flip = (flip, False)

        if hdr_render:
            shader = self._shader_tonemap

        # Get the vertex coordinates of a rectangle that has been rotated,
        # scaled, and translated, in world coordinates
        dest_vertices = create_rotated_rect(
            position, section.width, section.height, scale, angle, flip
        )

        # Convert the section rectangle into a list of vertices
        section_vertices = [
            (section.x, section.y),
            (section.x + section.width, section.y),
            (section.x, section.y + section.height),
            (section.x + section.width, section.y + section.height),
        ]

        # Render the texture
        self.render_from_vertices(tex, layer, dest_vertices, section_vertices, shader)

    def render_from_vertices(
        self,
        tex: Texture,
        layer: Layer,
        dest_vertices: list[tuple[float, float]],
        section_vertices: list[tuple[float, float]],
        shader: Shader = None,
    ) -> None:
        if shader is None:
            shader = self._shader_draw

        # Convert to destination coordinates (NDC)
        vertex_coords = [to_dest_coords(p, layer.width, layer.height) for p in dest_vertices]
        p1, p2, p3, p4 = vertex_coords
        vertex_data = np.array([p3, p4, p2, p2, p4, p1], dtype=np.float32)  # (6,2)

        # Texture UVs
        section_coords = [to_source_coords(p, tex.width, tex.height) for p in section_vertices]
        p1, p2, p3, p4 = section_coords
        section_data = np.array([p3, p4, p1, p1, p4, p2], dtype=np.float32)  # (6,2)

        # Interleave into (6,4): [x,y,u,v]
        buffer_data = np.hstack([vertex_data, section_data]).astype(np.float32, copy=False)

        # Upload
        self._quad_vbo.orphan(buffer_data.nbytes)
        self._quad_vbo.write(buffer_data.tobytes())

        # IMPORTANT: bind target + texture + sampler uniforms (this is what you were missing)
        layer.framebuffer.use()
        tex.use()
        shader.bind_sampler2D_uniforms()

        # VAO cache per program
        key = shader.program.glo
        vao = self._quad_vao_cache.get(key)
        if vao is None:
            vao = self._ctx.vertex_array(
                shader.program,
                [(self._quad_vbo, "2f 2f", "vertexPos", "vertexTexCoord")],
            )
            self._quad_vao_cache[key] = vao

        vao.render(moderngl.TRIANGLES)
        shader.clear_sampler2D_uniforms()

    def _coerce_instance_array(
        self, name: str, data, n_instances: int, components: int | None = None
    ) -> np.ndarray:
        arr = np.asarray(data, dtype=np.float32)
        if arr.ndim == 1:
            arr = arr.reshape(-1, 1)
        if arr.shape[0] != n_instances:
            raise ValueError(
                f"Length mismatch for '{name}': expected {n_instances}, got {arr.shape[0]}"
            )
        if components is not None and arr.shape[1] != components:
            raise ValueError(
                f"Component mismatch for '{name}': expected {components}, got {arr.shape[1]}"
            )
        return np.ascontiguousarray(arr, dtype=np.float32)

    def _resolve_instanced_shader(
        self,
        shader: Shader | None,
        hdr_render: bool,
        inferred_varyings: dict[str, int],
        instanced_uv_rect: bool,
    ) -> Shader:
        if shader is None:
            return self._shader_tonemap_instanced if hdr_render else self._shader_draw_instanced

        if not inferred_varyings:
            return shader

        if not getattr(shader, "_instanced_auto_infer_varyings", False):
            return shader

        key = (
            shader.program.glo,
            tuple(sorted(inferred_varyings.items())),
            instanced_uv_rect,
            getattr(shader, "_instanced_vertex_hook", ""),
        )
        cached = self._instanced_shader_variant_cache.get(key)
        if cached is not None:
            return cached

        variant = self.compile_shader(
            fragment_source=shader._instanced_fragment_source,
            instanced=True,
            instance_varyings=inferred_varyings,
            vertex_hook=shader._instanced_vertex_hook,
            instanced_uv_rect=instanced_uv_rect,
        )
        self._instanced_shader_variant_cache[key] = variant
        return variant

    def _shader_instance_attribute_name(self, shader: Shader, name: str) -> str:
        if name in ("uv_offset", "uv_scale"):
            return name
        if bool(getattr(shader, "_instanced_auto_vertex", False)):
            return f"a_{name}"
        return name

    def render_batch_instanced(
        self,
        tex: Texture,
        layer: Layer,
        positions: np.ndarray,
        scales: np.ndarray,
        angles: np.ndarray,
        shader: Shader = None,
        hdr_render: bool = False,
        instance_attributes: dict[str, np.ndarray] | None = None,
        uv_offset: np.ndarray | None = None,
        uv_scale: np.ndarray | None = None,
    ) -> None:
        """
        Render a sprite batch using GPU instancing.

        Angles are in radians. Built-in instanced shaders expect:
        - in vec2 position;
        - in vec2 scale;
        - in float angle;
        Extra attributes can be forwarded to the fragment shader as v_<name>.
        """
        positions = np.asarray(positions, dtype=np.float32)
        if positions.ndim != 2 or positions.shape[1] != 2:
            raise ValueError("positions must be shaped (N, 2)")
        n_instances = positions.shape[0]
        if n_instances == 0:
            return
        positions = self._coerce_instance_array(
            "position", positions, n_instances, components=2
        )
        scales = self._coerce_instance_array("scale", scales, n_instances, components=2)
        angles = self._coerce_instance_array("angle", angles, n_instances, components=1)

        # UV rect attributes must be supplied together.
        if (uv_offset is None) ^ (uv_scale is None):
            raise ValueError("uv_offset and uv_scale must be provided together")

        inferred_varyings = self._infer_instance_varyings(instance_attributes)
        use_instanced_uv_rect = uv_offset is not None and uv_scale is not None
        shader = self._resolve_instanced_shader(
            shader=shader,
            hdr_render=hdr_render,
            inferred_varyings=inferred_varyings,
            instanced_uv_rect=use_instanced_uv_rect,
        )

        attr_layout = list(self._DEFAULT_INSTANCED_ATTRS)
        attr_data = [positions, scales, angles]

        extras = dict(instance_attributes or {})
        if uv_offset is not None:
            extras["uv_offset"] = uv_offset
        if uv_scale is not None:
            extras["uv_scale"] = uv_scale

        for name, values in extras.items():
            self._validate_instance_attribute_name(name)
            arr = self._coerce_instance_array(name, values, n_instances)
            if arr.shape[1] < 1 or arr.shape[1] > 4:
                raise ValueError(
                    f"Instance attribute '{name}' must have 1-4 components"
                )
            attr_layout.append(
                (self._shader_instance_attribute_name(shader, name), int(arr.shape[1]))
            )
            attr_data.append(arr)

        total_floats = sum(components for _, components in attr_layout)
        stride_bytes = total_floats * np.dtype(np.float32).itemsize
        interleaved = np.empty((n_instances, total_floats), dtype=np.float32)
        offset = 0
        for arr in attr_data:
            components = arr.shape[1]
            interleaved[:, offset : offset + components] = arr
            offset += components

        cache_key = (
            shader.program.glo,
            tuple(attr_layout),
            use_instanced_uv_rect,
            stride_bytes,
        )
        cache = self._instanced_vao_cache.get(cache_key)

        if cache is None:
            instance_vbo = self._ctx.buffer(reserve=max(stride_bytes, 4))
            format_str = " ".join(f"{components}f" for _, components in attr_layout)
            attr_names = [name for name, _ in attr_layout]
            vao = self._ctx.vertex_array(
                shader.program,
                [
                    (self._instanced_base_pos_vbo, "2f", "vertexPos"),
                    (self._instanced_base_uv_vbo, "2f", "vertexTexCoord"),
                    (instance_vbo, f"{format_str}/i", *attr_names),
                ],
            )
            cache = {
                "instance_vbo": instance_vbo,
                "vao": vao,
                "capacity": 1,
                "stride_bytes": stride_bytes,
            }
            self._instanced_vao_cache[cache_key] = cache

        if cache["stride_bytes"] != stride_bytes:
            raise RuntimeError("Instanced cache stride mismatch")

        if cache["capacity"] < n_instances:
            while cache["capacity"] < n_instances:
                cache["capacity"] *= 2
            cache["vao"].release()
            cache["instance_vbo"].release()
            instance_vbo = self._ctx.buffer(
                reserve=max(cache["capacity"] * stride_bytes, 4)
            )
            format_str = " ".join(f"{components}f" for _, components in attr_layout)
            attr_names = [name for name, _ in attr_layout]
            cache["vao"] = self._ctx.vertex_array(
                shader.program,
                [
                    (self._instanced_base_pos_vbo, "2f", "vertexPos"),
                    (self._instanced_base_uv_vbo, "2f", "vertexTexCoord"),
                    (instance_vbo, f"{format_str}/i", *attr_names),
                ],
            )
            cache["instance_vbo"] = instance_vbo

        cache["instance_vbo"].orphan(max(cache["capacity"] * stride_bytes, 4))
        cache["instance_vbo"].write(interleaved.tobytes())

        tex.use()
        shader.bind_sampler2D_uniforms()
        layer.framebuffer.use()
        try:
            shader["screenSize"] = (layer.width, layer.height)
        except KeyError:
            pass
        cache["vao"].render(moderngl.TRIANGLES, instances=n_instances)
        shader.clear_sampler2D_uniforms()

    def render_primitive(
        self,
        layer: Layer,
        color: tuple,
        vertices: list[tuple[float, float]],
        antialias: bool = False,
        mode: int = moderngl.LINES,
    ):
        """
        Render a primitive shape (e.g., lines, triangles) on the specified layer.

        :param layer: The rendering layer.
        :param color: The color of the primitive in (R, G, B) or (R, G, B, A) format.
        :param vertices: A list of vertex coordinates as (x, y) tuples.
        :param antialias: Enables antialiasing if True.
        :param mode: The rendering mode (e.g., LINES, TRIANGLES).
        """
        if len(color) == 3:
            color = (color[0], color[1], color[2], 255)

        # Enable MSAA
        if antialias:
            pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 4)

        # Convert to destination coordinates
        dest_width, dest_height = layer.size
        dest_vertices = np.array(
            [to_dest_coords(v, dest_width, dest_height) for v in vertices]
        )

        # VBO and VAO
        vbo = self.ctx.buffer(dest_vertices.astype("f4").tobytes())
        vao = self.ctx.simple_vertex_array(self.prog_prim, vbo, "vert")

        # Send color uniform
        self.prog_prim["primColor"] = color

        # Set layer as target
        layer.framebuffer.use()

        # Render
        vao.render(mode)

        # Disable MSAA
        if antialias:
            pygame.display.gl_set_attribute(pygame.GL_MULTISAMPLESAMPLES, 1)

        # Free vertex data
        vbo.release()
        vao.release()

    def render_triangles(
        self,
        layer: Layer,
        color: tuple,
        vertices: list[tuple[float, float]],
        antialias: bool = False,
        strip: bool = False,
        fan: bool = False,
    ):
        """
        Render triangles on the specified layer.

        :param layer: The rendering layer.
        :param color: The color of the triangles in (R, G, B) or (R, G, B, A) format.
        :param vertices: A list of vertex coordinates as (x, y) tuples.
        :param antialias: Enables antialiasing if True.
        :param strip: If True, uses TRIANGLE_STRIP mode.
        :param fan: If True, uses TRIANGLE_FAN mode.
        """
        # Warn if both strip and fan flags are enabled simultaneously
        if strip and fan:
            warnings.warn(
                "Both strip and fan flags enabled. Overriding with strip flag."
            )

        # Pick the flag for the render mode
        if strip:
            flag = moderngl.TRIANGLE_STRIP
        elif fan:
            flag = moderngl.TRIANGLE_FAN
        else:
            flag = moderngl.TRIANGLES

        self.render_primitive(layer, color, vertices, antialias, flag)

    def render_lines(
        self,
        layer: Layer,
        color: tuple[float, float, float],
        vertices: list[tuple[float, float]],
        antialias: bool = False,
        strip: bool = False,
    ):
        """
        Render lines on the specified layer.

        :param layer: The rendering layer.
        :param color: The color of the lines in (R, G, B) or (R, G, B, A) format.
        :param vertices: A list of vertex coordinates as (x, y) tuples.
        :param antialias: Enables antialiasing if True.
        :param strip: If True, uses LINE_STRIP mode.
        """
        # Pick the flag for the render mode
        if strip:
            flag = moderngl.LINE_STRIP
        else:
            flag = moderngl.LINES

        self.render_primitive(layer, color, vertices, antialias, flag)

    def render_circle_arc(
        self,
        layer: Layer,
        color: tuple,
        center: tuple[float, float],
        radius: float,
        angle1: float,
        angle2: float,
        antialias: bool = False,
        num_segments: None | int = None,
    ):
        """
        Render a circular arc on the specified layer.

        :param layer: The rendering layer.
        :param color: The color of the arc in (R, G, B) or (R, G, B, A) format.
        :param center: The center of the arc as (x, y) tuple.
        :param radius: The radius of the arc.
        :param angle1: The starting angle of the arc in degrees.
        :param angle2: The ending angle of the arc in degrees.
        :param antialias: Enables antialiasing if True.
        :param num_segments: The number of segments to use for the arc. If None, defaults to a smooth arc.
        """
        # Ensure the arc always goes the shortest route
        if angle2 < angle1:
            angle2 += 360

        # If the number of segments is not provided, fix it to 32 segments per
        # 360 degrees, to get a smooth looking arc
        if num_segments == None:
            num_segments = max(4, int(32 * abs(angle2 - angle1) / 360))

        # Convert angles from degrees to radians
        angle1 = np.radians(angle1)
        angle2 = np.radians(angle2)

        # Include the center as the first vertex to render with TRIANGLE_FAN
        vertices = [center]

        # Generate the vertices
        for angle in np.linspace(angle1, angle2, num_segments + 1):

            # Calculate the x and y coordinates for each vertex
            x = center[0] + radius * cos(angle)
            y = center[1] + radius * sin(angle)

            vertices.append((x, y))

        # Render a triangle fan with the vertices
        self.render_primitive(layer, color, vertices, antialias, moderngl.TRIANGLE_FAN)

    def render_circle(
        self,
        layer: Layer,
        color: tuple,
        center: tuple[float, float],
        radius: float,
        antialias: bool = False,
        num_segments: int = None,
    ):
        """
        Render a full circle on the specified layer.

        :param layer: The rendering layer.
        :param color: The color of the circle in (R, G, B) or (R, G, B, A) format.
        :param center: The center of the circle as (x, y) tuple.
        :param radius: The radius of the circle.
        :param antialias: Enables antialiasing if True.
        :param num_segments: The number of segments to use for the circle. If None, defaults to a smooth circle.
        """
        self.render_circle_arc(
            layer, color, center, radius, 0, 360, antialias, num_segments
        )

    def render_rectangle(
        self,
        layer: Layer,
        color: tuple,
        position: tuple[float, float],
        width: float,
        height: float,
        angle: float = 0,
        antialias: bool = False,
    ):
        """
        Render a rectangle on the specified layer.

        :param layer: The rendering layer.
        :param color: The color of the rectangle in (R, G, B) or (R, G, B, A) format.
        :param position: The position of the rectangle's center as (x, y) tuple.
        :param width: The width of the rectangle.
        :param height: The height of the rectangle.
        :param angle: The rotation angle of the rectangle in degrees.
        :param antialias: Enables antialiasing if True.
        """
        vertices = create_rotated_rect(
            position, width, height, [1, 1], angle, [False, False]
        )
        v1, v2, v3, v4 = vertices
        self.render_primitive(
            layer, color, [v2, v3, v1, v4], antialias, moderngl.TRIANGLE_STRIP
        )

    def render_thick_line(
        self,
        layer: Layer,
        color: tuple,
        p1: tuple[float, float],
        p2: tuple[float, float],
        thickness: float,
        capped: bool = False,
        antialias: bool = False,
    ):
        """
        Render a thick line on the specified layer.

        :param layer: The rendering layer.
        :param color: The color of the line in (R, G, B) or (R, G, B, A) format.
        :param p1: The starting point of the line as (x, y) tuple.
        :param p2: The ending point of the line as (x, y) tuple.
        :param thickness: The thickness of the line.
        :param capped: If True, adds caps at the ends of the line.
        :param antialias: Enables antialiasing if True.
        """
        # Calculate direction vector and normalize it
        direction = (p2[0] - p1[0], p2[1] - p1[1])
        direction_norm = np.linalg.norm(direction)
        direction = direction / direction_norm

        # Calculate the perpendicular vector
        h_thickness = thickness / 2
        perpendicular = np.array([-direction[1], direction[0]]) * h_thickness

        # Calculate the four corners of the rectangle
        vertices = np.array(
            [
                p1 + perpendicular,
                p1 - perpendicular,
                p2 + perpendicular,
                p2 - perpendicular,
            ]
        )

        # Draw line segment as a rectangle
        self.render_primitive(
            layer, color, vertices, antialias, moderngl.TRIANGLE_STRIP
        )

        # Draw caps at both ends of the line segment
        if capped:
            angle = np.rad2deg(np.arctan2(direction[1], direction[0]))
            self.render_circle_arc(
                layer, color, p1, h_thickness, angle + 90, angle + 270, antialias
            )
            self.render_circle_arc(
                layer, color, p2, h_thickness, angle - 90, angle + 90
            )

    def render_text(
        self,
        font_atlas: FontAtlas,
        layer: Layer,
        text: str,
        letter_frame: int,
        color: tuple = (1.0, 1.0, 1.0, 1.0),
        scale: float = 1.0,
        alignment: str = None,
    ):
        """
        Render the text on the specified layer with an optional color.

        Parameters:
        - font_atlas: The font atlas.
        - layer: The rendering layer to draw on.
        - text: The text to render.
        - letter_frame: The number of letters to render (useful for animations).
        - color: The color of the text as an RGBA tuple. Default is white (1.0, 1.0, 1.0, 1.0).
        - scale: Multiplier for glyph size (1.0 = original size).
        - alignment: The alignment of the text, accepts None, 'left', 'center' and 'right'.
        """
        if len(color) == 3:
            color = (color[0], color[1], color[2], 1.0)

        if alignment == None:
            vertices = font_atlas.get_char_batch(
                layer.width, layer.height, text, letter_frame, scale
            )
        else:
            vertices = font_atlas.get_char_batch_aligned(
                layer.width, layer.height, text, letter_frame, scale, alignment
            )

        font_atlas.font_texture.use(location=0)  # Bind the font texture at location 0

        vbo = self._ctx.buffer(vertices.tobytes())
        vao = self._ctx.vertex_array(
            self._shader_text.program,
            [
                (vbo, "2f 2f", "vertexPos", "vertexTexCoord"),
            ],
        )

        self._shader_text.program["textColor"].value = (
            color  # Pass the color to the shader
        )

        layer.framebuffer.use()  # Bind the framebuffer

        vao.render(mode=self._ctx.TRIANGLES)

        # Cleanup after rendering
        vbo.release()
        vao.release()

    def release_opengl_resources(self):
        """
        Manually release OpenGL resources managed by the RenderEngine.

        Note:
        - Once this method is called, the engine is no longer usable.
        - This method is automatically called by the garbage collector,
          so there is no need to do it manually.
        """
        for cache in self._instanced_vao_cache.values():
            cache["vao"].release()
            cache["instance_vbo"].release()
        self._instanced_vao_cache.clear()
        for shader in self._instanced_shader_variant_cache.values():
            shader.release()
        self._instanced_shader_variant_cache.clear()
        self._instanced_base_pos_vbo.release()
        self._instanced_base_uv_vbo.release()

        self._shader_draw.release()
        self._shader_draw_instanced.release()
        self._shader_tonemap.release()
        self._shader_tonemap_instanced.release()
        self._shader_text.release()
        self._screen.framebuffer.release()
        self._ctx.release()

        self._shader_draw = None
        self._shader_draw_instanced = None
        self._shader_tonemap = None
        self._shader_tonemap_instanced = None
        self._shader_text = None
        self._screen = None
        self._ctx = None

        for vao in self._quad_vao_cache.values():
            vao.release()
        self._quad_vao_cache.clear()
        self._quad_vbo.release()             

    def __del__(self):
        # Check if ctx is None to avoid double-freeing
        if self._ctx != None:
            self.release_opengl_resources()
