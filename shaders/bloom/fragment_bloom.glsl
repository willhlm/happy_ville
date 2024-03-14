#version 330

// https://godotshaders.com/shader/bloom-post-processing-for-viewports/

in vec2 fragmentTexCoord; // holds the Vertex position <-1,+1> !!!
uniform sampler2D imageTexture; // used texture unit
out vec4 COLOR;

uniform float bloomRadius = 2; // Increase bloom radius
uniform float bloomThreshold = 0.7; // Adjust bloom threshold
uniform float bloomIntensity = 2; // Increase bloom intensity
uniform vec3 bloomTint = vec3(1.0, 1.0, 1.0); // Tint color for bloom -> if we want to tint it to a specific colour
uniform vec3 targetColor = vec3(0.39, 0.78, 1); // Target color for bloom
uniform float colorRange = 0.2; // Range around the target color for bloom: 1 means all colours

vec3 GetBloomPixel(sampler2D tex, vec2 uv, vec2 texPixelSize) {
    vec2 uv2 = floor(uv / texPixelSize) * texPixelSize;
    uv2 += texPixelSize * 0.001;
    vec3 tl = max(texture(tex, uv2).rgb - bloomThreshold, 0.0);
    vec3 tr = max(texture(tex, uv2 + vec2(texPixelSize.x, 0.0)).rgb - bloomThreshold, 0.0);
    vec3 bl = max(texture(tex, uv2 + vec2(0.0, texPixelSize.y)).rgb - bloomThreshold, 0.0);
    vec3 br = max(texture(tex, uv2 + vec2(texPixelSize.x, texPixelSize.y)).rgb - bloomThreshold, 0.0);
    vec2 f = fract(uv / texPixelSize);
    vec3 tA = mix(tl, tr, f.x);
    vec3 tB = mix(bl, br, f.x);
    return mix(tA, tB, f.y);
}

vec3 GetBloom(sampler2D tex, vec2 uv, vec2 texPixelSize) {
    vec3 bloom = vec3(0.0);
    vec2 off = vec2(1) * texPixelSize * bloomRadius;
    bloom += GetBloomPixel(tex, uv + off * vec2(-1, -1), texPixelSize * bloomRadius) * 0.292893;
    bloom += GetBloomPixel(tex, uv + off * vec2(-1, 0), texPixelSize * bloomRadius) * 0.5;
    bloom += GetBloomPixel(tex, uv + off * vec2(-1, 1), texPixelSize * bloomRadius) * 0.292893;
    bloom += GetBloomPixel(tex, uv + off * vec2(0, -1), texPixelSize * bloomRadius) * 0.5;
    bloom += GetBloomPixel(tex, uv + off * vec2(0, 0), texPixelSize * bloomRadius) * 1.0;
    bloom += GetBloomPixel(tex, uv + off * vec2(0, 1), texPixelSize * bloomRadius) * 0.5;
    bloom += GetBloomPixel(tex, uv + off * vec2(1, -1), texPixelSize * bloomRadius) * 0.292893;
    bloom += GetBloomPixel(tex, uv + off * vec2(1, 0), texPixelSize * bloomRadius) * 0.5;
    bloom += GetBloomPixel(tex, uv + off * vec2(1, 1), texPixelSize * bloomRadius) * 0.292893;
    bloom /= 4.171573f; // Normalize bloom contribution
    return bloom;
}

void main() {
    vec2 TEXTURE_PIXEL_SIZE = 1.0 / vec2(textureSize(imageTexture, 0).xy);
    vec2 UV = fragmentTexCoord;
    vec4 col = texture(imageTexture, UV);

    vec3 bloom = vec3(0.0);

    // Iterate over neighboring pixels -> to get the glow effect
    for (int i = -int(bloomRadius); i <= int(bloomRadius); i++) {
        for (int j = -int(bloomRadius); j <= int(bloomRadius); j++) {
            vec2 neighborUV = UV + vec2(i, j) * TEXTURE_PIXEL_SIZE;

            // Sample the color of the neighboring pixel
            vec4 neighborColor = texture(imageTexture, neighborUV);

            // Calculate the difference between the neighboring pixel color and the target color
            float colorDifference = length(neighborColor.rgb - targetColor);

            // Check if the neighboring pixel color matches the target color
            if (colorDifference <= colorRange) {
                // Calculate the bloom effect for the neighboring pixel
                vec3 neighborBloom = GetBloom(imageTexture, neighborUV, TEXTURE_PIXEL_SIZE);

                // Apply bloom tint
                neighborBloom *= bloomTint;

                // Accumulate the bloom effect
                bloom += neighborBloom;
            }
        }
    }

    // Modify the alpha channel based on bloom intensity
    float alpha = clamp(col.a + max(max(bloom.r, bloom.g), bloom.b) * bloomIntensity, 0.0, 1.0);

    // Apply the accumulated bloom effect to the pixel
    col.rgb += bloom * bloomIntensity;
    col.a = alpha;

    COLOR = col;
}
