#version 330 core

in vec2 fragmentTexCoord;

uniform sampler2D imageTexture;
uniform sampler2D SCREEN_TEXTURE;

uniform float time = 0.0;
uniform vec2 resolution = vec2(64.0, 64.0);
uniform vec4 section = vec4(0.0, 0.0, 64.0, 64.0);

uniform vec4 shine_color = vec4(0.82, 0.92, 1.0, 0.92);
uniform float reveal = 0.0;
uniform float reveal_softness = 0.16;
uniform float distortion_strength = 18.0;
uniform float distortion_frequency = 4.5;
uniform float silhouette_alpha = 0.82;

out vec4 color;

vec2 hash(vec2 p) {
    p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)));
    return fract(sin(p) * 43758.5453123);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);

    return mix(
        mix(
            dot(hash(i + vec2(0.0, 0.0)), f - vec2(0.0, 0.0)),
            dot(hash(i + vec2(1.0, 0.0)), f - vec2(1.0, 0.0)),
            f.x
        ),
        mix(
            dot(hash(i + vec2(0.0, 1.0)), f - vec2(0.0, 1.0)),
            dot(hash(i + vec2(1.0, 1.0)), f - vec2(1.0, 1.0)),
            f.x
        ),
        f.y
    );
}

float fbm(vec2 p) {
    float value = 0.0;
    float amplitude = 0.5;

    for (int i = 0; i < 4; i++) {
        value += noise(p) * amplitude;
        p = p * 2.03 + vec2(13.7, 9.2);
        amplitude *= 0.5;
    }

    return value * 0.5 + 0.5;
}

void main() {
    vec2 uv = fragmentTexCoord;
    vec4 base = texture(imageTexture, uv);
    float centerAlpha = base.a;

    if (centerAlpha <= 0.0) {
        color = vec4(0.0);
        return;
    }

    vec2 screenSize = vec2(textureSize(SCREEN_TEXTURE, 0));
    vec2 normalizedSectionPos = vec2(section.x, section.y) / screenSize;
    vec2 normalizedSectionSize = vec2(section.z, section.w) / screenSize;
    vec2 sectionOrigin = vec2(
        normalizedSectionPos.x,
        1.0 - normalizedSectionPos.y - normalizedSectionSize.y
    );
    vec2 screenUV = uv * normalizedSectionSize + sectionOrigin;
    vec2 screenPixelSize = 1.0 / max(screenSize, vec2(1.0));

    vec2 centered = uv - 0.5;
    float aspect = resolution.x / max(resolution.y, 1.0);
    vec2 aspectCoord = vec2(centered.x * aspect, centered.y);
    vec2 radialDir = length(aspectCoord) > 0.0001 ? normalize(aspectCoord) : vec2(0.0, 0.0);
    vec2 tangent = vec2(-radialDir.y, radialDir.x);

    float flowA = fbm(uv * distortion_frequency + vec2(time * 0.8, -time * 0.55));
    float flowB = fbm((uv.yx + 0.31) * (distortion_frequency * 0.87) + vec2(-time * 0.6, time * 0.45));
    float flowC = fbm((uv + vec2(flowA, flowB) * 0.12) * (distortion_frequency * 0.65) + time * 0.3);

    vec2 distortion = vec2(flowA - 0.5, flowB - 0.5);
    distortion += tangent * ((flowC - 0.5) * 1.7);
    distortion += radialDir * (sin(time * 2.1 + flowA * 6.2831) * 0.6);

    float revealNoise = fbm(uv * 5.5 + vec2(time * 0.2, -time * 0.18));
    float revealMask = smoothstep(revealNoise - reveal_softness, revealNoise + reveal_softness, reveal);
    float distortionMask = centerAlpha * (1.0 - revealMask);

    float shineSweep = sin((uv.y - uv.x * 0.45) * 12.0 - time * 3.5);
    float shineBand = smoothstep(0.55, 0.98, shineSweep);
    float shineNoise = fbm(uv * 9.0 + vec2(time * 0.9, -time * 0.7));
    float shineFlicker = smoothstep(0.62, 0.9, shineNoise);
    float coreLight = smoothstep(0.55, 0.05, length(aspectCoord));
    float shineMask = shineBand * shineFlicker * coreLight * distortionMask;

    vec2 refractedUV = clamp(
        screenUV + distortion * distortion_strength * screenPixelSize * distortionMask,
        0.0,
        1.0
    );
    vec4 refracted = texture(SCREEN_TEXTURE, refractedUV);

    vec3 spectralTint = mix(vec3(0.36, 0.56, 0.92), shine_color.rgb, flowA);
    vec3 spiritRgb = mix(refracted.rgb, refracted.rgb + spectralTint * 0.14, distortionMask);
    spiritRgb += shine_color.rgb * shineMask * 0.75;
    vec3 revealedRgb = mix(spiritRgb, base.rgb, revealMask);

    float finalAlpha = centerAlpha * max(silhouette_alpha * (1.0 - revealMask), revealMask);
    vec3 finalRgb = revealedRgb;

    color = vec4(finalRgb, finalAlpha);
}
