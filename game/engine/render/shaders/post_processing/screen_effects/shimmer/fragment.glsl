#version 330 core

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;

uniform sampler2D noiseTexture;
uniform float time;

// Tuning (start here)
uniform float grainStrength = 0.035;   // 0.02–0.06
uniform float shimmerStrength = 0.04;  // 0.02–0.08
uniform float vignetteStrength = 0.18; // 0.10–0.30
uniform float shimmerSpeed = 0.25;     // 0.10–0.40

out vec4 color;

float luma(vec3 c) { return dot(c, vec3(0.299, 0.587, 0.114)); }

void main()
{
    vec2 uv = fragmentTexCoord;

    // Base sample (no warp)
    vec4 base = texture(imageTexture, uv);

    // Screen-space noise UV (tileable)
    vec2 nUV = uv * vec2(2.0, 2.0) + 0 * vec2(time * 0.01, time * 0.013);
    float n = texture(noiseTexture, nUV).r;          // 0..1
    float n2 = texture(noiseTexture, nUV * 2.7).r;   // extra detail

    // Grain (centered around 0)
    float grain = (n - 0.5) * 2.0 * grainStrength;

    // Shimmer: affect mainly bright pixels (stars, highlights)
    float lum = luma(base.rgb);
    float highlightMask = smoothstep(0.55, 0.90, lum); // only bright areas
    float shimmer = (sin(time * shimmerSpeed + n2 * 6.2831) * 0.5 + 0.5); // 0..1
    float shimmerOffset = (shimmer - 0.5) * 2.0 * shimmerStrength * highlightMask;

    // Vignette
    vec2 p = uv - 0.5;
    float vig = smoothstep(0.85, 0.20, dot(p, p)); // 1 center -> 0 edges
    float vigFactor = mix(1.0 - vignetteStrength, 1.0, vig);

    vec3 rgb = base.rgb;
    rgb += grain;           // tiny grain
    rgb += shimmerOffset;   // subtle highlight twinkle
    rgb *= vigFactor;       // slight vignette

    color = vec4(rgb, base.a);
}
