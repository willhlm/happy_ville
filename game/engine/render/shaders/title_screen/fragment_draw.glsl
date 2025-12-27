#version 330 core

in vec2 fragmentTexCoord;

// Time uniform
uniform float time;

// === CUSTOMIZABLE UNIFORMS ===

// Base colors
uniform vec3 baseVoidColor = vec3(0.015, 0.02, 0.035);
uniform vec3 fogColorTint = vec3(0.12, 0.15, 0.22);
uniform vec3 rayColorTint = vec3(0.18, 0.22, 0.3);

// Fog settings
uniform float fogSpeed1 = 0.02;
uniform float fogSpeed2 = 0.015;
uniform float fogSpeed3 = 0.025;
uniform float fogIntensity = 1.0;
uniform float fogContrast = 1.5;

// Particle settings
uniform float particleSpawnThreshold = 0.85; // Higher = fewer particles (0.0 to 1.0)
uniform float particleSpeed1 = 0.2;
uniform float particleSpeed2 = 0.15;
uniform float particleSpeed3 = 0.1;
uniform float particleMinSize = 0.1;
uniform float particleMaxSize = 0.3;
uniform vec3 particleColor1 = vec3(0.8, 0.9, 1.0);
uniform vec3 particleColor2 = vec3(0.7, 0.85, 1.0);
uniform vec3 particleColor3 = vec3(0.9, 0.95, 1.0);
uniform float particleLayer1Intensity = 0.6;
uniform float particleLayer2Intensity = 0.4;
uniform float particleLayer3Intensity = 0.5;

// Light orb settings
uniform int lightCount = 12;
uniform float lightSpeed = 0.03;
uniform float lightCoreSize = 0.15;
uniform float lightGlowSize = 0.5;
uniform vec3 warmLightColor = vec3(1.0, 0.85, 0.6);
uniform vec3 coolLightColor = vec3(0.5, 0.7, 1.0);
uniform float lightIntensity = 0.8;
uniform float fogLightInteraction = 0.6;

// Vignette settings
uniform float vignetteStrength = 0.5;
uniform float vignetteStart = 0.3;
uniform float vignetteEnd = 1.3;
uniform float vignettePower = 0.8;

// Depth gradient
uniform float depthGradientStrength = 0.25;

// Animation settings
uniform float pulseSpeed = 0.3;
uniform float pulseIntensity = 0.015;

// Ray settings
uniform float rayIntensity = 0.08;

out vec4 color;

// Hash function for better randomness
float hash(vec2 p) {
    p = fract(p * vec2(123.34, 456.21));
    p += dot(p, p + 45.32);
    return fract(p.x * p.y);
}

float hash13(vec3 p3) {
    p3 = fract(p3 * 0.1031);
    p3 += dot(p3, p3.zyx + 31.32);
    return fract((p3.x + p3.y) * p3.z);
}

// 2D Noise
float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

// Fractal Brownian Motion
float fbm(vec2 p, int octaves) {
    float value = 0.0;
    float amplitude = 0.5;
    float frequency = 1.0;
    
    for(int i = 0; i < octaves; i++) {
        value += amplitude * noise(p * frequency);
        frequency *= 2.1;
        amplitude *= 0.45;
    }
    return value;
}

// Domain warping
vec2 warp(vec2 p, float amount) {
    return p + vec2(
        fbm(p + vec2(time * 0.1, time * 0.05), 3),
        fbm(p + vec2(time * 0.07, -time * 0.08), 3)
    ) * amount;
}

// Smooth fade-in/fade-out function
float lifetimeFade(float normalizedLifetime) {
    // Fade in over first 15%, fade out over last 15%
    float fadeIn = smoothstep(0.0, 0.15, normalizedLifetime);
    float fadeOut = smoothstep(1.0, 0.85, normalizedLifetime);
    return fadeIn * fadeOut;
}

// Improved particle system with smooth lifetime fading
float particles(vec2 p, float seed, float speed) {
    // Account for aspect ratio in the grid to keep particles circular
    vec2 aspectCorrectedP = p;
    aspectCorrectedP.x *= 640.0 / 360.0;
    
    vec2 gridP = aspectCorrectedP * 8.0;
    vec2 gridI = floor(gridP);
    vec2 gridF = fract(gridP);
    
    float particleField = 0.0;
    
    for(int y = -1; y <= 1; y++) {
        for(int x = -1; x <= 1; x++) {
            vec2 neighbor = vec2(float(x), float(y));
            vec2 cellId = gridI + neighbor;
            
            // Random properties for each cell
            float randSeed = hash(cellId + seed);
            
            // Only spawn particle if random is high enough
            if(randSeed > particleSpawnThreshold) {
                // Random position within cell
                vec2 offset = vec2(
                    hash(cellId + 0.1),
                    hash(cellId + 0.2)
                );
                
                // Chaotic movement
                float timeOffset = hash(cellId + 0.3) * 6.28;
                float moveSpeed = 0.5 + hash(cellId + 0.4) * 1.5;
                float lifetime = hash(cellId + 0.7) * 100.0; // Random start offset
                
                vec2 movement = vec2(
                    sin(time * moveSpeed * 0.3 + timeOffset) * 0.3,
                    -time * speed * moveSpeed + lifetime
                );
                
                // Calculate particle's lifetime (0 to 1, wrapping)
                float particleLife = fract(movement.y);
                movement.y = particleLife;
                
                // SMOOTH FADE IN/OUT based on lifetime
                float lifetimeMask = lifetimeFade(particleLife);
                
                vec2 particlePos = neighbor + offset + movement - gridF;
                float dist = length(particlePos);
                
                // Random size using uniform parameters
                float size = particleMinSize + hash(cellId + 0.6) * (particleMaxSize - particleMinSize);
                
                // Individual brightness for each particle (not synchronized)
                float baseBrightness = 0.6 + hash(cellId + 0.8) * 0.4;
                float pulseSpeedVar = 0.5 + hash(cellId + 0.9) * 2.0;
                float pulsePhase = hash(cellId + 1.0) * 6.28;
                float brightness = baseBrightness * (0.7 + 0.3 * sin(time * pulseSpeedVar + pulsePhase));
                
                float particle = smoothstep(size, 0.0, dist);
                
                // Apply lifetime fade to prevent popping
                particleField += particle * brightness * lifetimeMask;
            }
        }
    }
    
    return particleField;
}

// Glowing lights/lanterns with individual lifetime tracking
float lights(vec2 p, float seed, out vec3 lightColorOut) {
    float lightField = 0.0;
    lightColorOut = vec3(0.0);
    
    // Create several floating lights - each individually tracked
    for(int i = 0; i < lightCount; i++) {
        float fi = float(i) + seed;
        
        // Individual lifetime for each light
        float lightLifetime = hash13(vec3(fi, seed, 2.0)) * 100.0;
        float lightSpeedVar = lightSpeed + hash13(vec3(fi, seed, 3.0)) * lightSpeed;
        
        // Calculate this light's current lifetime (0 to 1)
        float life = fract((time * lightSpeedVar) + lightLifetime);
        
        // Smooth fade in/out for this specific light
        float lifetimeMask = lifetimeFade(life);
        
        // Each light has its own path
        vec2 lightPos = vec2(
            sin(time * 0.15 + fi * 0.8) * 1.2 + sin(time * 0.3 + fi) * 0.4,
            life * 2.5 - 0.5  // Use lifetime for Y position
        );
        
        // Figure-8 or circular motion
        lightPos.x += cos(time * 0.2 + fi * 1.3) * 0.3;
        
        float dist = length(p - lightPos);
        
        // Core glow
        float core = smoothstep(lightCoreSize, 0.0, dist) * 0.8;
        
        // Outer glow (larger, softer)
        float glow = smoothstep(lightGlowSize, 0.0, dist) * 0.3;
        
        // Individual pulsing for each light
        float pulse = 0.7 + 0.3 * sin(time * 1.5 + fi * 2.0);
        
        // Individual color per light
        float colorSeed = hash13(vec3(fi, seed, 4.0));
        vec3 lightColor;
        
        if(colorSeed < 0.5) {
            lightColor = warmLightColor;
        } else {
            lightColor = coolLightColor;
        }
        
        // Apply lifetime fade to this light
        float intensity = (core + glow) * pulse * lifetimeMask;
        
        lightField += intensity;
        lightColorOut += lightColor * intensity;
    }
    
    // Normalize color
    if(lightField > 0.0) {
        lightColorOut /= lightField;
    }
    
    return lightField;
}

void main()
{
    // Normalize coordinates
    vec2 uv = fragmentTexCoord;
    uv.y = 1.0 - uv.y;
    vec2 p = uv * 2.0 - 1.0;
    p.x *= 640.0 / 360.0;
    
    // === BASE VOID COLOR ===
    vec3 baseColor = baseVoidColor;
    
    // === LAYERED FOG ===
    vec2 warpedUV1 = warp(uv * 1.5 + vec2(time * fogSpeed1, 0.0), 0.3);
    vec2 warpedUV2 = warp(uv * 2.0 - vec2(time * fogSpeed2, time * 0.01), 0.4);
    vec2 warpedUV3 = warp(uv * 0.8 + vec2(0.0, time * fogSpeed3), 0.5);
    
    float fog1 = fbm(warpedUV1, 6);
    float fog2 = fbm(warpedUV2, 5);
    float fog3 = fbm(warpedUV3, 4);
    
    float fogCombined = (fog1 * 0.5 + fog2 * 0.3 + fog3 * 0.2) * fogIntensity;
    fogCombined = pow(fogCombined, fogContrast);
    
    vec3 fogColor = fogColorTint * fogCombined;
    
    // === VOLUMETRIC RAYS ===
    float rays = 0.0;
    vec2 rayUV = uv;
    rayUV.x += sin(uv.y * 3.0 + time * 0.1) * 0.1;
    
    for(int i = 0; i < 3; i++) {
        float offset = float(i) * 0.3;
        float ray = abs(sin((rayUV.x + offset) * 3.14159 * 2.0 + time * 0.05));
        ray = pow(ray, 8.0);
        ray *= fbm(rayUV * 2.0 + time * 0.05, 3) * 0.5;
        rays += ray;
    }
    rays *= rayIntensity;
    vec3 rayColor = rayColorTint * rays;
    
    // === CHAOTIC PARTICLES WITH SMOOTH FADING ===
    vec2 pUV = uv;
    
    // Layer 1: Small, fast particles
    float particles1 = particles(pUV, 1.0, particleSpeed1);
    
    // Layer 2: Medium particles with different timing
    float particles2 = particles(pUV * 0.7, 2.5, particleSpeed2);
    
    // Layer 3: Slow, drifting particles
    float particles3 = particles(pUV * 1.3, 4.2, particleSpeed3);
    
    // Different colors for particle layers
    vec3 particleColor1Val = particleColor1 * particles1 * particleLayer1Intensity;
    vec3 particleColor2Val = particleColor2 * particles2 * particleLayer2Intensity;
    vec3 particleColor3Val = particleColor3 * particles3 * particleLayer3Intensity;
    
    vec3 particleColor = particleColor1Val + particleColor2Val + particleColor3Val;
    
    // === FLOATING LIGHTS WITH INDIVIDUAL TRACKING ===
    vec2 lightUV = p;
    vec3 lightColor;
    float lightField = lights(lightUV, 0.0, lightColor);
    
    // Apply the calculated color
    vec3 finalLightColor = lightColor * lightField * lightIntensity;
    
    // === LIGHT GLOW ON FOG (interaction) ===
    vec3 fogLightInteractionColor = fogColor * lightField * fogLightInteraction;
    
    // === VIGNETTE ===
    float vignette = length(p) * vignetteStrength;
    vignette = 1.0 - smoothstep(vignetteStart, vignetteEnd, vignette);
    vignette = pow(vignette, vignettePower);
    
    // === DEPTH GRADIENT ===
    float depth = smoothstep(0.0, 0.7, uv.y) * depthGradientStrength;
    
    // === COMBINE ALL LAYERS ===
    vec3 finalColor = baseColor;
    finalColor += fogColor;
    finalColor += fogLightInteractionColor;
    finalColor += rayColor;
    finalColor += particleColor;
    finalColor += finalLightColor;
    finalColor *= vignette;
    finalColor -= depth;
    
    // === SUBTLE PULSING ===
    float pulse = sin(time * pulseSpeed) * pulseIntensity + 1.0;
    finalColor *= pulse;
    
    // === COLOR GRADING ===
    finalColor = pow(finalColor, vec3(1.05));
    finalColor = clamp(finalColor, 0.0, 1.0);
    
    color = vec4(finalColor, 1.0);
}
