#version 330 core

//https://godotshaders.com/shader/2d-fog-overlay-2/

in vec2 fragmentTexCoord;  // Texture coordinates
out vec4 COLOR;

uniform sampler2D imageTexture;  // Texture sampler
uniform float TIME;  // Time

// Noise texture
uniform sampler2D noise_texture;
// Fog speed
uniform vec2 speed = vec2(0.5,0);
uniform vec4 skycolour1 = vec4(0.5, 0.3, 0.3, 1); // bottom
uniform vec4 skycolour2 =  vec4(0, 0.4, 0.6, 1); // top
uniform vec4 cloudcolour = vec4(0.9, 0.9, 0.9, 1);
uniform vec2 scroll;

// Called for every pixel the material is visible on
void main() {
    // Make the fog slowly move
    vec2 uv = fragmentTexCoord + speed * TIME * 0.1*fragmentTexCoord.y + 0.01*fragmentTexCoord.y*scroll/vec2(640,360);
    // Sample the noise texture
    float noise = texture(noise_texture, uv).r;
    // Convert the noise from the (0.0, 1.0) range to the (-1.0, 1.0) range
    // and clamp it between 0.0 and 1.0 again
    float fog = clamp(fragmentTexCoord.y*noise * 3.0 - 0.3, 0.0, 1.0);
    // Apply the fog effect

    // Mix the sky colors based on the fragment's y-coordinate
    vec4 skycolour = mix(skycolour1, skycolour2, fragmentTexCoord.y);

    // Calculate the final color by mixing cloud color with the mixed sky color
    vec4 blended_color = mix(skycolour, cloudcolour, fog);

    COLOR = blended_color;
}
