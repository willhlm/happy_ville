#version 330 core

layout(location = 0) in vec3 vertexPos;      // Vertex position (in pixels)
layout(location = 1) in vec2 vertexTexCoord; // Texture coordinates

uniform vec2 camera_offset;  // Camera scroll offset (in pixels)
uniform vec2 parallax;       // Parallax scaling factor
uniform vec2 screen_size = vec2(640,360);    // Screen resolution (width, height)

out vec2 fragmentTexCoord;

void main() {
    // Convert camera offset to normalized device coordinates (NDC)
    vec2 offset_ndc = (camera_offset * parallax) / screen_size * 2.0; // Scale to [-1, 1]

    // Flip Y direction for OpenGL clip space
    offset_ndc.y = -offset_ndc.y;  

    // Adjust vertex position
    vec3 adjustedPos = vertexPos;
    adjustedPos.xy += offset_ndc; // Apply corrected camera offset

    // Convert to clip space (-1 to 1 range)
    gl_Position = vec4(adjustedPos, 1.0);

    // Pass texture coordinates to the fragment shader
    fragmentTexCoord = vertexTexCoord;
}
