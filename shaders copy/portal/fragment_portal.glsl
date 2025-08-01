#version 330 core

// https://godotshaders.com/shader/ring-of-power/

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;
out vec4 COLOR;

uniform float TIME;
uniform sampler2D noise;
uniform sampler2D screen;

uniform float radius;
uniform float thickness = 0.2;
uniform vec4 color = vec4(0.39, 0.78, 1, 1.0);
uniform float brightness = 5.0;
uniform float angular_speed = 2.5;
uniform float radial_speed = 1.4;
uniform float alpha = 0.5;

const vec2 screenSize = vec2(640.0, 340.0)/2;

void main() {
    vec2 UV = fragmentTexCoord;
    // Calculate the size of each pixel in UV space
    vec2 pixelSize = 1.0 / screenSize;
    // Quantize texture coordinates for pixelation effect
    UV = floor(UV / pixelSize) *pixelSize;
    
    vec2 v = vec2(.5) - UV;
    float d = length(v) * 2.;
    float angle = atan(v.y, v.x) + (TIME * angular_speed);
    float thick_ratio = 1. - (abs(d - max(0., radius)) / max(.0001, thickness));
    vec2 polar = fract(vec2(angle / 6.28, d + (TIME * radial_speed)));
    vec4 col = color * thick_ratio; //thick_ratio * brightness * color;
    vec3 tex = texture(noise, polar).rgb;
    col.a = brightness * (alpha * (tex.r + tex.g + tex.b) * clamp(thick_ratio, 0., 1.)) / 3.;

    COLOR = vec4(col.xyz / col.a, col.a);
}