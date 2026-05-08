#version 330

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;
out vec4 COLOR;

uniform vec3 glowColor = vec3(1.0, 0, 0.0); // Orange glow
uniform float glowIntensity = 2.0;
uniform vec2 radialCenter = vec2(0.5, 0.5);
uniform float radialInner = 0.0;
uniform float radialOuter = 0.2;

void main() {
    vec4 originalColor = texture(imageTexture, fragmentTexCoord);
    float dist = distance(fragmentTexCoord, radialCenter);
    float radialMask = 1.0 - smoothstep(radialInner, radialOuter, dist);
    vec4 glow = vec4(glowColor * radialMask, radialMask);

    vec3 finalRgb = originalColor.rgb + glow.rgb * glowIntensity;
    float finalAlpha = max(originalColor.a, clamp(glow.a * glowIntensity, 0.0, 1.0));
    COLOR = vec4(finalRgb, finalAlpha);
}
