#version 330 core

in vec2 fragmentTexCoord; // Texture coordinate from the vertex shader
uniform float time; // Current time
uniform vec2 textureSize; // Size of the texture

uniform sampler2D noiseTexture; // Perlin noise texture

// Particle parameters
uniform vec4 baseParticleColor = vec4(1,1,1,1); // Base color of the particles
uniform float spawnRate = 10; // Rate at which particles spawn (particles per second)
uniform float baseParticleRadius = 0.05; // Base radius of the particle
uniform float baseParticleSpeed = 0.2; // Base speed of upward movement
uniform float particleLifetime = 2.0; // Lifetime of each particle in seconds
uniform float horizontalSpread = 0.5; // Horizontal spread of particle movement
uniform vec2 spawnPosition = vec2(0.5, 0.0); // Mid-bottom of the texture

uniform float radiusVariation = 0.02; // Variation in particle radius
uniform float edgeFalloff = 0.02; // Edge falloff distance
uniform float colorVariation = 0.2; // Variation in particle color

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

    // Calculate spawn interval based on spawn rate
    float spawnInterval = 1.0 / spawnRate; // Time between each new particle spawn

    // Initialize color accumulator
    vec4 accumulatedColor = vec4(0.0); // Initialize particle color to transparent

    // Loop to create multiple particles
    float maxParticles = ceil(particleLifetime / spawnInterval); // Max number of particles alive at once
    for (float i = max(0.0, ceil(time / spawnInterval) - maxParticles); i < ceil(time / spawnInterval); i += 1.0) {
        float particleAge = time - i * spawnInterval;

        // Seed for randomness
        float seed = i * 0.1; // Unique seed for each particle

        // Calculate random initial direction and speed for each particle
        vec2 randomDirection = vec2((fract(sin(seed) * 12.9898) * 2.0 - 1.0) * horizontalSpread, 1.0); // Horizontal spread and always moving upwards
        float randomSpeed = baseParticleSpeed + fract(sin(seed + 1.0) * 43758.5453) * 0.1; // Random speed variation

        // Compute the position of the particle based on its initial direction and speed
        vec2 particlePosition = spawnPosition + randomDirection * (particleAge * randomSpeed);

        // Randomize radius for each particle and keep it constant during its lifetime
        float radius = baseParticleRadius + fract(sin(seed + 2.0) * 43758.5453) * radiusVariation; // Random radius

        // Randomize color for each particle and keep it constant during its lifetime
        vec3 particleColor = baseParticleColor.rgb + (fract(sin(seed + 3.0) * 43758.5453) - 0.5) * colorVariation; // Random color

        // Introduce a particle-specific noise offset
        vec2 noiseOffset = vec2(fract(sin(seed + 4.0) * 43758.5453) * 2.0 - 1.0, fract(sin(seed + 5.0) * 43758.5453) * 2.0 - 1.0);

        // Sample the noise texture to get the noise value
        vec2 noiseUV = (uv - particlePosition + noiseOffset);
        float noiseValue = texture(noiseTexture, noiseUV).r; // Sample the noise texture (using the red channel)

        // Compute particle opacity with noise effect
        float alpha = 1.0 - smoothstep(0.0, particleLifetime, particleAge); // Fade out over lifetime
        float particleAlpha = circle(uv, particlePosition, radius, aspectRatio) * alpha * noiseValue;

        // Set the particle color and alpha using the uniform
        vec4 particleColorVec4 = vec4(particleColor, particleAlpha); // Use randomized color and adjust alpha

        // Accumulate color using alpha blending
        vec3 blendedColor = accumulatedColor.rgb * (1.0 - particleColorVec4.a) + particleColorVec4.rgb * particleColorVec4.a;
        float finalAlpha = accumulatedColor.a + particleColorVec4.a * (1.0 - accumulatedColor.a);
        
        accumulatedColor = vec4(blendedColor, finalAlpha);
    }

    // Output the final color
    color = accumulatedColor;
}
