#version 330 core

in vec2 fragmentTexCoord; // top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture; // texture in location 0

uniform int octaves = 2; // Amount of detail.
uniform float starting_amplitude = 0.3; // Opacity of the output fog.
uniform float starting_frequency = 0.5; // Rate of pattern within the fog.
uniform float shift = -0.1; // Shift towards transparency (clamped) for sparser fog.
uniform vec2 velocity = vec2(1.0, 0.0); // Direction and speed of travel.
uniform vec4 fog_color = vec4(1, 1, 1, 0.5); // Color of the fog.

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
        output_2 += texture(noise, uv * frequency).x * amplitude;
        amplitude /= 2.0;
        frequency *= 2.0;
    }
    return clamp(output_2 + shift, 0.0, 1.0);
}

uniform float damping = 0.1; // Damping factor to smooth out scrolling motion

void main() {
    vec2 UV = fragmentTexCoord - scroll;
    vec2 smoothedScroll = mix(scroll, UV, damping); // Smooth out scrolling motion
    vec2 motion = vec2(rand(smoothedScroll + TIME * starting_frequency * velocity));
    COLOR = mix(vec4(1, 1, 1, 0), fog_color, rand(smoothedScroll + motion));
}
