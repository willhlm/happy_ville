#version 330 core

layout(location = 0) in vec3 vertexPos;      // Vertex position (in pixels)
layout(location = 1) in vec2 vertexTexCoord; // Texture coordinates

out vec2 fragmentTexCoord;

// Vertex shader for scaling up to display
uniform vec2 u_screen_size;    // Screen size (e.g., 640x360)
uniform float u_scale;         // Scale factor (e.g., 2.0)
uniform vec2 u_camera_offset;  // Camera fractional offset

void main()
{
    vec4 pos = vec4(vertexPos, 1.0);
    
    // Convert from NDC to screen coordinates
    vec2 screenPos = (pos.xy + 1.0) * 0.5 * u_screen_size;
    
    // Apply camera offset and scale to get display coordinates
    vec2 displayPos = screenPos * u_scale + u_camera_offset * u_scale;
    
    // Ensure alignment with display pixels
    displayPos = floor(displayPos + 0.5);
    
    // Calculate display resolution from screen size and scale
    vec2 displayResolution = u_screen_size * u_scale;
    
    // Convert back to NDC using display resolution
    pos.xy = (displayPos / displayResolution) * 2.0 - 1.0;
    
    gl_Position = pos;
    fragmentTexCoord = vertexTexCoord;
}