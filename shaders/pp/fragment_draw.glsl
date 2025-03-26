
#version 330 core

uniform sampler2D tex;          // The rendered game scene
uniform vec2 screen_size;       // Screen resolution
uniform float pixel_size;       // Size of each snapped pixel
uniform vec2 parallax;          // Parallax factors for X and Y directions

in vec2 fragmentTexCoord;// top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture;// texture in location 0

out vec4 fragColor;

void main() {
    // Convert UV coordinates to screen-space position
    vec2 screen_pos = fragmentTexCoord * screen_size * parallax;

    // Snap the position to the nearest grid based on the pixel size
    screen_pos = floor(screen_pos / pixel_size) * pixel_size;

    // Convert the snapped position back to normalized UV coordinates
    vec2 snapped_uv = screen_pos / (screen_size * parallax);

    // Sample the texture at the snapped coordinates
    fragColor = texture(tex, snapped_uv);
}
