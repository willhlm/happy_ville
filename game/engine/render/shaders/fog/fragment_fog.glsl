#version 330 core

in vec2 fragmentTexCoord; // top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture; // texture in location 0

uniform int octaves = 1; // Amount of detail.
uniform float starting_amplitude = 1; // Opacity of the output fog.
uniform float starting_frequency = 0.5; // Rate of pattern within the fog.
uniform float shift = 0; // Shift towards transparency (clamped) for sparser fog.
uniform vec2 velocity = vec2(2.0, 0.0); // Direction and speed of travel.
uniform vec4 fog_color = vec4(1, 1, 1, 1); // Color of the fog.

uniform sampler2D noise; // Noise texture; OpenSimplexNoise is great, but any filtered texture is fine.
uniform vec2 resolution = vec2(640, 360);
uniform float TIME;
uniform vec2 scroll;

out vec4 COLOR;

float rand(vec2 uv) {
    float amplitude = starting_amplitude;
    float frequency = starting_frequency;
    float output_2 = 0.0;
    for (int i = 0; i < octaves; i++) {
        output_2 += texture(noise, uv*0.2 - vec2(0.8*scroll.x,1.2*scroll.y)/resolution).x * amplitude*frequency;
        amplitude /= 2.0;
        frequency *= 2.0;
    }
    return clamp(output_2 + shift, 0.0, 1.0);
}

void main() {
    vec2 UV = fragmentTexCoord;
    vec2 shiftedUV = UV - scroll/resolution; // Apply shift only to noise texture sampling coordinates
    vec2 motion = vec2(rand(UV + TIME * starting_frequency * velocity));

    float noise_value = rand(UV + motion);
    COLOR = vec4(fog_color.rgb, fog_color.a * noise_value);

//    COLOR = mix(vec4(1, 1, 1, 0), fog_color, rand(UV + motion)); // Use shiftedUV for noise texture sampling
}
