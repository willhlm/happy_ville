#version 330

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;
out vec4 COLOR;

uniform float glowRadius = 5.0;
uniform vec3 glowColor = vec3(1.0, 0, 0.0); // Orange glow
uniform vec3 targetColor = vec3(1,1,1); // Red objects will glow
uniform float glowIntensity = 2.0;
uniform float colorTolerance = 1; // How close colors need to be
uniform float glowThreshold = 0; // minimum brightness

vec3 GetGlow(sampler2D tex, vec2 uv, vec2 texPixelSize) {
    vec3 glow = vec3(0.0);
    int radius = int(glowRadius);
    float totalWeight = 0.0;
    
    for (int y = -radius; y <= radius; y++) {
        for (int x = -radius; x <= radius; x++) {
            vec2 offset = vec2(x, y) * texPixelSize;
            vec3 sample = texture(tex, uv + offset).rgb;
            
            // Check color similarity to target
            float colorDistance = distance(normalize(sample), normalize(targetColor));
            float colorMatch = 1.0 - smoothstep(0.0, colorTolerance, colorDistance);
            
            // Optional: also check brightness
            float brightness = dot(sample, vec3(0.299, 0.587, 0.114));
            float brightnessCheck = step(glowThreshold, brightness);
            
            float glowMask = colorMatch * brightnessCheck;
            
            // Distance-based weight for smooth falloff
            float distance = length(vec2(x, y));
            float weight = 1.0 / (1.0 + distance * 0.1);
            
            glow += glowColor * glowMask * weight;
            totalWeight += weight;
        }
    }
    
    return glow / totalWeight;
}

void main() {
    vec2 TEXTURE_PIXEL_SIZE = 1.0 / vec2(textureSize(imageTexture, 0).xy);
    
    vec4 originalColor = texture(imageTexture, fragmentTexCoord);
    vec3 glow = GetGlow(imageTexture, fragmentTexCoord, TEXTURE_PIXEL_SIZE);
    
    COLOR = vec4(originalColor.rgb + glow * glowIntensity, originalColor.a);
}