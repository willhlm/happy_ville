#version 330 core

uniform float radius;     // Radius of the circle (in pixels)
uniform vec4 color;       // Color of the circle (RGBA)
uniform float gradient;   // If there should be a gradient: 1 for yes, 0 for no

vec4 norm_color; // Store the normalized output color

in vec2 fragmentTexCoord; // Texture coordinates (in [0, 1] range)
out vec4 fragColor;

void main() {
    // Calculate the distance from the center of the texture (normalized coordinates [0.5, 0.5])
    vec2 center = vec2(0.5, 0.5); // Texture center (normalized)
    float distance = length(fragmentTexCoord - center); // Calculate distance from center (in normalized space)

    // Normalize the color (color values are in [0, 255] range, so divide by 255)
    norm_color = color / vec4(255.0); // Normalize color to [0, 1]
    
    // Apply gradient if needed: fade alpha based on distance from center
    norm_color.w *= (1 - gradient*distance/radius) * step(distance,radius);//change alpha.

    // Output the final fragment color
    fragColor = norm_color;
}
