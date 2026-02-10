#version 330 core

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;

out vec4 COLOR;
uniform float TIME;

uniform float AuraProgres = 0.8;
uniform float AuraSize = 0.2; // How far the aura extends
uniform float AnimSpeed = 2.0;
uniform float NoiseScale = 8.0;
uniform vec3 aura_color = vec3(0.3, 0.7, 1.0); // Cyan aura
uniform float NoiseIntensity = 5; // How much noise affects aura shape
uniform float AuraFalloff = 2.0; // Controls how sharp the aura edge is (higher = sharper)

// Better noise function for smoother animation
float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float smoothNoise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f); // Smooth interpolation
    
    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));
    
    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

// Fractal noise for more organic look
float fractalNoise(vec2 p) {
    float value = 0.0;
    float amplitude = 0.5;
    
    for(int i = 0; i < 4; i++) {
        value += amplitude * smoothNoise(p);
        p *= 2.0;
        amplitude *= 0.5;
    }
    
    return value;
}

vec4 createAura(vec2 uv, vec4 spriteColor) {
    vec2 texelSize = 1.0 / textureSize(imageTexture, 0);
    
    // Check if we're inside the sprite
    float centerAlpha = spriteColor.a;
    if(centerAlpha > 0.1) {
        return spriteColor; // Show original sprite
    }
    
    // Find distance to nearest sprite pixel
    float minDist = 999.0;
    bool foundSprite = false;
    
    // Sample in a radius around current pixel - extend search beyond AuraSize for smoother transition
    int radius = int(AuraSize * 60.0); // Slightly larger search radius
    for(int x = -radius; x <= radius; x++) {
        for(int y = -radius; y <= radius; y++) {
            vec2 offset = vec2(float(x), float(y)) * texelSize;
            vec2 sampleUV = uv + offset;
            
            if(sampleUV.x >= 0.0 && sampleUV.x <= 1.0 && 
               sampleUV.y >= 0.0 && sampleUV.y <= 1.0) {
                float sampleAlpha = texture(imageTexture, sampleUV).a;
                
                if(sampleAlpha > 0.1) {
                    float dist = length(offset) / AuraSize;
                    minDist = min(minDist, dist);
                    foundSprite = true;
                }
            }
        }
    }
    
    // Instead of hard cutoff, use gradual falloff that extends beyond 1.0
    if(!foundSprite || minDist > 1.5) { // Extended range for smoother transition
        return vec4(0.0); // No aura here
    }
    
    // Create animated noise for shape variation
    vec2 animUV1 = uv * NoiseScale + vec2(TIME * AnimSpeed * 0.3, TIME * AnimSpeed * 0.2);
    vec2 animUV2 = uv * NoiseScale * 1.3 + vec2(-TIME * AnimSpeed * 0.2, TIME * AnimSpeed * 0.4);
    vec2 animUV3 = uv * NoiseScale * 0.7 + vec2(TIME * AnimSpeed * 0.1, -TIME * AnimSpeed * 0.3);
    
    float noise1 = fractalNoise(animUV1);
    float noise2 = fractalNoise(animUV2);
    float noise3 = fractalNoise(animUV3);
    
    // Combine noises for complex animation
    float combinedNoise = (noise1 + noise2 * 0.7 + noise3 * 0.5) / 2.2;
    
    // Create pulsing effect (more subtle)
    float pulse = 0*sin(TIME * AnimSpeed * 0.8) * 0.15 + 0.85;
    
    // Use multiple layers of noise to create organic, wispy aura shape
    vec2 flowOffset1 = vec2(TIME * 0.2, TIME * 0.15);
    vec2 flowOffset2 = vec2(-TIME * 0.18, TIME * 0.22);
    vec2 flowOffset3 = vec2(TIME * 0.12, -TIME * 0.28);
    
    float shapeNoise1 = fractalNoise(uv * NoiseScale * 0.6 + flowOffset1);
    float shapeNoise2 = fractalNoise(uv * NoiseScale * 1.2 + flowOffset2);
    float detailNoise = fractalNoise(uv * NoiseScale * 2.5 + flowOffset3);
    
    // Combine noises to create irregular aura boundaries
    float combinedShapeNoise = (shapeNoise1 * 0.6 + shapeNoise2 * 0.3 + detailNoise * 0.1);
    
    // Apply noise to modify the distance field
    float noisyDistance = minDist - (combinedShapeNoise - 0.5) * NoiseIntensity * 0.3;
    
    // IMPROVED: Gradual distance-based falloff using smoothstep
    // Create multiple falloff zones for more natural transition
    float innerFalloff = 1.0 - smoothstep(0.0, 0.6, noisyDistance);  // Strong inner aura
    float outerFalloff = 1.0 - smoothstep(0.4, 1.2, noisyDistance);  // Gentle outer fade
    float edgeFalloff = 1.0 - smoothstep(0.8, 1.5, noisyDistance);   // Very soft edge
    
    // Combine falloffs with different weights
    float combinedFalloff = innerFalloff * 0.7 + outerFalloff * 0.2 + edgeFalloff * 0.1;
    combinedFalloff = pow(max(combinedFalloff, 0.0), AuraFalloff);
    
    // Create additional wispy details
    float wispNoise = fractalNoise(uv * NoiseScale * 4.0 + flowOffset1 * 2.0);
    float wispiness = mix(0.7, 1.0, wispNoise);
    
    // Add distance-based opacity variation for more natural look
    float distanceOpacity = 1.0 - smoothstep(0.0, 1.0, minDist * 0.8);
    
    // Final aura strength with smooth falloff
    float auraStrength = combinedFalloff * wispiness * pulse * AuraProgres * distanceOpacity;
    auraStrength = clamp(auraStrength, 0.0, 1.0);
    
    // Create flowing color variations
    float colorShift = fractalNoise(uv * 3.0 + TIME * 0.5) * 0.3;	
    vec3 finalColor = aura_color + vec3(colorShift * 0.2, colorShift * 0.1, -colorShift * 0.1);
    
    // Add subtle color variation based on distance for depth
    float distanceColorShift = smoothstep(0.0, 1.0, minDist);
    finalColor = mix(finalColor * 1.2, finalColor * 0.8, distanceColorShift);
    
    return vec4(finalColor, auraStrength);
}

void main() {
    vec4 spriteColor = texture(imageTexture, fragmentTexCoord);
    vec4 result = createAura(fragmentTexCoord, spriteColor);
    
    // Blend sprite over aura
    COLOR = mix(result, spriteColor, spriteColor.a);
}