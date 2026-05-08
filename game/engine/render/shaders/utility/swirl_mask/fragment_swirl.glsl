#version 330 core

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;

uniform vec2 center = vec2(0.5, 0.5);
uniform float turns = 3.0;
uniform float radial_bias = 1.0;
uniform float angle_offset = 0.0;

out vec4 COLOR;

void main()
{
    vec2 uv = fragmentTexCoord - center;
    float radius = length(uv) * 1.41421356237;
    float angle = atan(uv.y, uv.x);
    float spiral = (angle + 3.14159265359) / 6.28318530718;
    spiral += radius * turns + angle_offset;
    spiral = fract(spiral);

    float luminance = mix(spiral, radius, clamp(radial_bias, 0.0, 1.0));
    luminance = clamp(luminance, 0.0, 1.0);
    COLOR = vec4(vec3(luminance), 1.0);
}
