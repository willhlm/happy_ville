#version 330

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;
out vec4 COLOR;

uniform float bloomRadius = 10.0;
uniform float bloomThreshold = 0.1;
uniform float bloomIntensity = 10.0;

vec3 GetBloom(sampler2D tex, vec2 uv, vec2 texPixelSize) {
    vec3 bloom = vec3(0.0);
    int radius = int(bloomRadius);
    
    // Two-pass separable blur for efficiency
    // Horizontal pass
    for (int y = -radius; y <= radius; y++) {
        vec3 h_sum = vec3(0.0);
        for (int x = -radius; x <= radius; x++) {
            vec2 offset = vec2(x, y) * texPixelSize;
            vec3 sample = texture(tex, uv + offset).rgb;
            // Only bloom bright pixels
            h_sum += max(sample - bloomThreshold, 0.0);
        }
        bloom += h_sum / float((radius * 2 + 1));
    }
    
    bloom /= float((radius * 2 + 1));
    return bloom;
}

void main() {
    vec2 TEXTURE_PIXEL_SIZE = 1.0 / vec2(textureSize(imageTexture, 0).xy);
    
    vec4 col = texture(imageTexture, fragmentTexCoord);
    vec3 bloom = GetBloom(imageTexture, fragmentTexCoord, TEXTURE_PIXEL_SIZE);
    col.rgb += bloom * bloomIntensity;
    COLOR = col;
}