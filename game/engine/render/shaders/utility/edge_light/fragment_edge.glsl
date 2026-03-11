#version 330 core

in vec2 fragmentTexCoord; // Texture coordinates passed from vertex shader
uniform sampler2D imageTexture; // Texture containing the entities
uniform sampler2D textureNoise; // Noise texture
uniform float TIME;
uniform vec2 screenSize = vec2(640,360); // Screen dimensions

uniform float radius = 0.459;
uniform float effectControl = 0.309;
uniform float burnSpeed = 0.076;

out vec4 COLOR;

void main() {
    vec2 UV = fragmentTexCoord;

    // Sample alpha value of the entities
    float alpha = texture(imageTexture, UV).a;

    // Edge detection: compare alpha with neighbors
    vec2 pixelSize = 1.0 / screenSize;
    float alphaLeft = texture(imageTexture, UV + vec2(-pixelSize.x, 0)).a;
    float alphaRight = texture(imageTexture, UV + vec2(pixelSize.x, 0)).a;
    float alphaUp = texture(imageTexture, UV + vec2(0, pixelSize.y)).a;
    float alphaDown = texture(imageTexture, UV + vec2(0, -pixelSize.y)).a;

    // Compute edge strength
    float edgeStrength = max(
        max(abs(alpha - alphaLeft), abs(alpha - alphaRight)),
        max(abs(alpha - alphaUp), abs(alpha - alphaDown))
    );

    // Apply noise border effect only at edges
    float noiseValue = texture(textureNoise, vec2(UV.x,1-UV.y) + vec2(0, burnSpeed * TIME)).r;
    float opacity = smoothstep(0.1, 0.3, edgeStrength) * noiseValue;
    COLOR = vec4(1.0, 1.0, 1.0, opacity);

}
