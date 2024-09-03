#version 330 core

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;

uniform vec2 refraction_stretch = vec2(1.0, 1.0);
uniform float refraction_strength = 0.02;
uniform float speed = 0.1;

uniform vec4 liquid_tint;
uniform vec4 darker_color; // New uniform for the darker region
uniform vec4 line_color; // New uniform for the line color

uniform sampler2D SCREEN_TEXTURE;
uniform sampler2D refraction_map;
uniform vec2 u_resolution;
uniform vec4 section;
uniform float TIME;

uniform float lineHeightPixels = 5.0; // Line height in pixels
uniform float darkerRegionHeightPixels = 6.0; // Darker region height in pixels

out vec4 COLOR;
vec4 new_liquid_tint;

// Function to generate wave displacement, modulated by the noise from refraction_map
float wave(vec2 uv, vec2 texture_size) {
    // Scale the wave frequency and amplitude by the texture size to make it independent
    float frequency = 10 * (texture_size.x / 1024.0); // Adjust frequency based on texture width
    float amplitude = 0.002 * (1024.0 / texture_size.y); // Adjust amplitude based on texture height

    float baseWave = sin(uv.x * frequency + TIME * speed * 5.0) * amplitude;
    float noise = texture(refraction_map, uv * 2.0).r;
    noise = (noise - 0.5) * amplitude;
    return baseWave + noise;
}

void main()
{
    vec2 uv = fragmentTexCoord;

    // Get the texture size using the built-in function
    vec2 texture_size = vec2(textureSize(imageTexture, 0));

    // Convert pixel heights to texture coordinates using the texture size
    float lineHeight = lineHeightPixels / texture_size.y;
    float darkerRegionHeight = darkerRegionHeightPixels / texture_size.y;

    // Calculate wave effect with noise using the refraction map
    float waveEffect = wave(uv, texture_size);

    // Position for the wavy line
    float waveLinePosition = 1.0 - lineHeight + waveEffect;

    if (uv.y > waveLinePosition) {
        // Top portion remains transparent
        COLOR = vec4(0.0, 0.0, 0.0, 0.0); // Fully transparent
        return;
    }
    else if (uv.y > (waveLinePosition - darkerRegionHeight * 0.95)) { // Line region
        new_liquid_tint = mix(darker_color, liquid_tint, (uv.y - (waveLinePosition - darkerRegionHeight * 0.95)) / darkerRegionHeight);
    }
    else if (uv.y > (waveLinePosition - darkerRegionHeight)) { // Darker region
        new_liquid_tint = mix(line_color, liquid_tint, (uv.y - (waveLinePosition - darkerRegionHeight)) / darkerRegionHeight);
    }
    else {
        new_liquid_tint = liquid_tint;
    }

    vec2 refraction_offset = texture(
        refraction_map, 
        vec2(
            mod(uv.x * refraction_stretch.x + TIME * speed, 1.0), 
            mod(uv.y * refraction_stretch.y + TIME * speed, 1.0))
    ).xy;

    refraction_offset -= 0.5; // Set values between -0.5 and 0.5 (instead of 0 and 1).

    // Get the screen texture and distort it
    vec2 normalizedSectionPos = vec2(section.x, section.y) / u_resolution;
    vec2 normalizedSectionSize = vec2(section.z, section.w) / u_resolution;
    vec2 screenUV = uv * normalizedSectionSize + vec2(normalizedSectionPos.x, 1.0 - normalizedSectionPos.y - normalizedSectionSize.y);

    vec4 refraction = texture(SCREEN_TEXTURE, screenUV - refraction_offset * refraction_strength);
    
    vec4 color = vec4(1.0);
    color.rgb = mix(refraction.rgb, new_liquid_tint.rgb, new_liquid_tint.a);
    
    COLOR = color;
}
