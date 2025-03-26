#version 330 core

uniform vec2 screen_size = vec2(640, 360);  // Screen resolution
uniform vec2 parallax = vec2(1.0, 1.0);     // Parallax factors for X and Y directions
uniform vec2 camera_offset = vec2(0.0, 0.0); // Camera scroll offset

in vec2 fragmentTexCoord;  // UV coordinates (0 to 1 range)
uniform sampler2D imageTexture;  // Texture sampler

out vec4 fragColor;

void main() {
    // Compute the per-pixel size in UV space
    vec2 pixel_size = 1.0 / screen_size;  

    // Compute world-space position (adjusted for parallax)
    vec2 world_pos = (fragmentTexCoord * screen_size) + (camera_offset * parallax);

    // Snap to a **global pixel grid**, ensuring all layers align
    vec2 snapped_world_pos = floor(world_pos / pixel_size) * pixel_size;

    // Convert back to UV space for texture sampling
    vec2 snapped_uv = (snapped_world_pos - (camera_offset * parallax)) / screen_size;

    // Sample the texture at the snapped UV coordinates
    fragColor = texture(imageTexture, snapped_uv);
}
