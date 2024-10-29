#version 330 core

in vec2 fragmentTexCoord; // Texture coordinate from the vertex shader

uniform sampler2D noiseTexture; // Perlin noise texture
uniform float time; // Current time
uniform vec2 textureSize; // Size of the texture

// Particle parameters for explosion
uniform vec4 baseParticleColor = vec4(1, 0.6, 0.1, 1); // Initial bright explosion color (orange/red)
uniform float baseParticleRadius = 0.05; // Smaller initial radius for particles
uniform float baseParticleSpeed = 1; // Initial speed for explosion particles
uniform float particleLifetime = 2.0; // Lifetime for explosion particles
uniform vec2 explosionCenter = vec2(0.5, 0.5); // Explosion starts from the center

uniform float radiusVariation = 0.02; // Variation in particle size
uniform float edgeFalloff = 0.05; // Smooth falloff at the edges of particles
uniform float colorVariation = 0.3; // Higher variation in particle color
uniform int numParticles = 100; // Total number of particles emitted at once

out vec4 color;

// Function to calculate particle opacity, accounting for aspect ratio
float circle(vec2 uv, vec2 position, float radius, vec2 aspectRatio) {
    vec2 scaledUV = (uv - position) / aspectRatio; // Scale UV coordinates to account for aspect ratio
    return smoothstep(radius, radius - edgeFalloff, length(scaledUV));
}

void main() {
    vec2 uv = fragmentTexCoord;

    // Aspect ratio calculation
    vec2 aspectRatio = vec2(textureSize.y / textureSize.x, 1.0); // Aspect ratio correction

    // Initialize color accumulator
    vec4 accumulatedColor = vec4(0.0); // Initialize particle color to transparent

    // Loop to create a fixed number of particles
    for (int i = 0; i < numParticles; i++) {
        // Seed for randomness
        float seed = float(i) * 0.1; // Unique seed for each particle

        // Calculate random initial direction for each particle (explosion is radial)
        float angle = fract(sin(seed) * 43758.5453) * 6.283185; // Random angle (0 to 2π for full circular motion)
        vec2 randomDirection = vec2(cos(angle), sin(angle)); // Radial movement in all directions

        // Particle age based on explosion time
        float particleAge = min(time, particleLifetime); // Clamp age to lifetime
        float speed = 1 - smoothstep(0, 1, particleAge );
        // Compute the position of the particle based on its initial direction and speed
        vec2 particlePosition = explosionCenter + randomDirection * (speed * baseParticleSpeed); // Constant speed

        // Radius gradually increases with time
        float radius = baseParticleRadius * (1.0 + particleAge) + fract(sin(seed + 2.0) * 43758.5453) * radiusVariation;

        // Color transition from bright (orange/red) to darker (grey) over time
        vec3 startColor = vec3(1.0, 0.4, 0.1); // Bright orange/red color at the start
        vec3 endColor = vec3(0.3, 0.3, 0.3);  // Dark grey color at the end
        vec3 particleColor = mix(startColor, endColor, particleAge / particleLifetime);

        // Introduce a particle-specific noise offset
        vec2 noiseOffset = vec2(fract(sin(seed + 4.0) * 43758.5453) * 2.0 - 1.0, fract(sin(seed + 5.0) * 43758.5453) * 2.0 - 1.0);

        // Sample the noise texture to get the noise value
        vec2 noiseUV = (uv - particlePosition + noiseOffset);
        float noiseValue = texture(noiseTexture, noiseUV).r; // Sample the noise texture (using the red channel)

        // Compute particle opacity with noise effect and fade it over time
        float alpha = 1.0 - smoothstep(0.0, particleLifetime, particleAge); // Gradually fade over lifetime
        float particleAlpha = circle(uv, particlePosition, radius, aspectRatio) * alpha * noiseValue;

        // Set the particle color and alpha using the uniform
        vec4 particleColorVec4 = vec4(particleColor, particleAlpha); // Apply color and alpha to the particle

        // Accumulate color using alpha blending
        vec3 blendedColor = accumulatedColor.rgb * (1.0 - particleColorVec4.a) + particleColorVec4.rgb * particleColorVec4.a;
        float finalAlpha = accumulatedColor.a + particleColorVec4.a * (1.0 - accumulatedColor.a);

        accumulatedColor = vec4(blendedColor, finalAlpha);
    }

    // Output the final color
    color = accumulatedColor;
}
