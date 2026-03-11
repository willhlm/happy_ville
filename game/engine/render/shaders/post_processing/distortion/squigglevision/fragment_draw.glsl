#version 330 core

in vec2 fragmentTexCoord; // UV coordinates
uniform sampler2D imageTexture; // main texture
uniform sampler2D noiseTexture; // noise texture for squiggle effect

// Squiggle parameters
uniform vec2 scale = vec2(1);//size of the chunks
uniform float strength =0.5;//intensity
uniform float fps = 0.1;//refresh rate
uniform float time; // You'll need to pass this from your application

out vec4 color;

// Constants
#define PI 3.14159265359
#define E 2.71828182846

void main()
{
    // For simple 2D without world coordinates, use screen-space UVs
    // This creates a screen-space squiggle pattern
    vec2 noiseSize = vec2(textureSize(noiseTexture, 0));
    vec2 noise_uv = fragmentTexCoord / scale;
    
    // Animate noise sampling over time
    vec2 offset_multiplier = vec2(PI, E);
    vec2 noise_offset = vec2(floor(time * fps)) * offset_multiplier;
    
    // Sample noise and convert to direction vector
    float noise_sample = texture(noiseTexture, noise_uv + noise_offset).r * 4.0 * PI;
    vec2 direction = vec2(cos(noise_sample), sin(noise_sample));
    
    // Apply squiggle distortion to UV coordinates
    vec2 squiggle_uv = fragmentTexCoord + direction * strength * 0.005;
    
    // Sample main texture with distorted UVs
    color = texture(imageTexture, squiggle_uv);
}