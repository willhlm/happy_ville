#version 330 core

in vec2 fragmentTexCoord; // top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture; // texture in location 0

out vec4 COLOR;

uniform vec2 player_position; // Player position in screen coordinates
uniform vec4 ambient; // Ambient color
uniform vec2 resolution; // Screen resolution

uniform float SCALE = 0.5;
uniform float SOFTNESS = 0.5;

void main(){
    // Convert fragmentTexCoord to pixel coordinates
    vec2 pixelCoord = fragmentTexCoord * resolution;

    // Calculate the distance from the player position
    float dist = distance(pixelCoord, vec2(player_position.x,resolution.y - player_position.y));

    // Normalize distance by SCALE and resolution
    float vignetteFactor = dist / (resolution.x * SCALE);

    // Calculate vignette effect using smoothstep
    float vignette = 1 - smoothstep(0.0, SOFTNESS, vignetteFactor);

    // Apply vignette effect to the background color
    COLOR = vec4(vignette, vignette, vignette, vignette); // Use vignette value for RGB and keep alpha as 1.0
}
