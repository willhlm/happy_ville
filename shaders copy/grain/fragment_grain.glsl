#version 330 core

in vec2 fragmentTexCoord;// top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture;// texture in location 0

out vec4 COLOR;
uniform vec2 SCREEN_UV = vec2 (640,360);
uniform float grain_amount = 0.02; // Adjust the amount of grain
uniform float grain_size = 0.5; // Adjust the size of the grain
uniform float time;

void main() {
    // Sample the original screen texture
    vec2 UV = fragmentTexCoord;
    vec4 original_color = texture(imageTexture, fragmentTexCoord);

    // Generate random noise
    float noise = (fract(sin(time*dot(UV, vec2(12.9898, 78.233))) * 43758.5453) - 0.5) * 2.0;

    // Add noise to the original color
    original_color.rgb += noise * grain_amount * grain_size;

    // Clamp the final color to make sure it stays in the valid range
    COLOR = clamp(original_color, 0.0, 1.0);
}
