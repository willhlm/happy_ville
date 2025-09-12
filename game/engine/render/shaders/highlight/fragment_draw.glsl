#version 330 core

in vec2 fragmentTexCoord;// top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture;// texture in location 0

//https://godotshaders.com/shader/2d-controlled-shine-highlight-with-angle-adjustment/

uniform vec4 shine_color = vec4(1, 1, 1, 0.8);
uniform float shine_progress = 0.0;
uniform float speed = 1;
uniform float shine_size  = 0.1;
uniform float shine_angle  = 45.0;

out vec4 COLOR;

float scale(float value, float inMin, float inMax, float outMin, float outMax) {
    return (value - inMin) * (outMax - outMin) / (inMax - inMin) + outMin;
}

void main() {
    COLOR = texture(imageTexture, fragmentTexCoord);
	float slope = tan(radians(shine_angle));
	float progress = scale( min(speed * shine_progress, 1), 0.0, 1.0, -1.0 - shine_size - shine_size * slope, 1.0 * slope);
    float shine = step(slope * fragmentTexCoord.x - fragmentTexCoord.y, progress + shine_size + shine_size * slope) - step(slope * fragmentTexCoord.x - fragmentTexCoord.y, progress);
    COLOR.rgb = mix(COLOR.rgb, shine_color.rgb, shine * shine_color.a);
}