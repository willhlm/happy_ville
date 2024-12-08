#version 330 core

in vec2 fragmentTexCoord; // Texture coordinates
uniform sampler2D imageTexture; // Main image texture
uniform sampler2D noise;        // Noise texture for distortion
uniform sampler2D maskTexture;  // Mask texture controlling distortion
out vec4 COLOR;                 // Final output color

uniform float TIME;             // Time variable for animation
uniform float speed = 0.3;      // Speed of distortion animation
uniform float size = 0.01;      // Scale of the distortion
uniform vec2 u_resolution = vec2(640,360);      // Screen resolution
uniform vec2 center; // Center of the distortion in normalized coordinates
uniform vec3 tint = vec3(1.0, 1.0, 1.0); // Tint for grayscale output

void main() {
    // Convert center from normalized coordinates to texture space
    vec2 normalizedCenter = vec2(center.x / u_resolution.x, 1.0 - center.y / u_resolution.y);

    // Compute offset relative to the center
    vec2 offset = fragmentTexCoord - normalizedCenter;

    // Compute distance from the center normalized to the screen diagonal
    float distanceFromCenter = length(offset);

    // Sample the mask texture to determine distortion strength
    vec2 maskUV = fragmentTexCoord - normalizedCenter;
    float maskValue = texture(maskTexture, maskUV).r; // Grayscale mask value (0.0 to 1.0)

    // Modulate distortion by mask value
    float distortionStrength = maskValue;

    // Add a time-varying offset to the texture coordinates based on noise
    vec2 smoke_uv = fragmentTexCoord + TIME * speed * distortionStrength;
    vec4 smoke_color = texture(noise, fract(smoke_uv));

    // Apply distortion scaled by tshe strength
    smoke_color = clamp(smoke_color * size * distortionStrength * distanceFromCenter * distanceFromCenter, 0.0, 1.0);

    // Distort the texture coordinates of the main image based on the noise
    vec4 img_color = texture(imageTexture, fragmentTexCoord + vec2(smoke_color.g - size * distanceFromCenter * distortionStrength / 2.0, 0.0));

    // Convert img_color to grayscale
    float luminance = dot(img_color.rgb, vec3(0.299, 0.587, 0.114));
    img_color.rgb = vec3(luminance) * tint;

    // Mix between distorted and original color based on the mask value
    vec4 original_color = texture(imageTexture, fragmentTexCoord);
    COLOR = mix(original_color, img_color, distortionStrength);
}
