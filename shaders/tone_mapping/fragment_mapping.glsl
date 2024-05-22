#version 330 core

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;

out vec4 colour; // This is the color uniform

// Exposure for tone mapping
uniform float exposure = 1;

void main() {
    vec3 hdrColor = texture(imageTexture, fragmentTexCoord).rgb;
    
    // Reinhard tone mapping
    vec3 mapped = hdrColor / (hdrColor + vec3(1.0));

    // Exposure adjustment
    mapped = vec3(1.0) - exp(-mapped * exposure);

    colour = vec4(mapped, 1.0)*texture(imageTexture, fragmentTexCoord).a;
}