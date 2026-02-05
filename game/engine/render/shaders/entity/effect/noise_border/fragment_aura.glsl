#version 330 core

in vec2 fragmentTexCoord; // Top-left is [0, 1], bottom-right is [1, 0]
uniform sampler2D imageTexture; // Texture for moon's surface

out vec4 COLOR;
uniform float TIME; 

uniform sampler2D textureNoise;
uniform float radius = 0.459;
uniform float effectControl = 0.509;
uniform float burnSpeed = 1;
uniform float shape = 0.1;

void main() {
    vec2 UV = fragmentTexCoord;
    vec2 centerDistVec = vec2(0.5) - UV;
    
	float distToCircleEdge = length(centerDistVec) * radius;
	float distToSquareEdge = 0.5*(0.5 - min(min(UV.x, 1.0 - UV.x), min(UV.y, 1.0 - UV.y)));
	float distToEdge = mix(distToCircleEdge,distToSquareEdge,shape);

    float gradient = smoothstep(0.5, 0.5 - radius, distToEdge);

    vec2 direction = vec2(0, 1) * burnSpeed;
    float noiseValue = texture(textureNoise, UV + direction * TIME).r;

    float opacity = step(radius, mix(gradient, noiseValue, effectControl) - distToEdge);

    COLOR = texture(imageTexture, UV) * vec4(1.0, 1.0, 1.0, opacity);
}
