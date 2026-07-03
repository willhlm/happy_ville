#version 330 core

in vec2 fragmentTexCoord; // top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture; // texture in location 0
uniform sampler2D SCREEN_TEXTURE;

uniform float time = 0.0;
uniform vec2 resolution = vec2(800.0, 600.0);
uniform vec4 albedo = vec4(1.0, 0.5, 0.3, 1.0);
uniform vec2 center = vec2(0.5, 0.5);
uniform vec4 section = vec4(0.0, 0.0, 800.0, 600.0);

out vec4 color;

const float nudge = 0.739513;
const float normalizer = 1.0 / sqrt(1.0 + nudge * nudge);

float SpiralNoiseC(vec3 p) {
    float n = 0.0;
    float iter = 1.0;

    for (int i = 0; i < 8; i++) {
        n += -abs(sin(p.y * iter) + cos(p.x * iter)) / iter;
        p.xy += vec2(p.y, -p.x) * nudge;
        p.xy *= normalizer;
        p.xz += vec2(p.z, -p.x) * nudge;
        p.xz *= normalizer;
        iter *= 1.733733;
    }

    return n;
}

float NebulaNoise(vec3 p, float anim) {
    p.xy += vec2(
        sin(anim * 0.9 + p.z * 0.7),
        cos(anim * 0.7 + p.x * 0.5)
    ) * 0.18;
    p.z += sin(anim * 0.5 + p.y * 0.6) * 0.35;

    float final = p.y + 4.5;
    final -= SpiralNoiseC(p.xyz);
    final += SpiralNoiseC(p.zxy * 0.5123 + 100.0 + vec3(anim * 0.06)) * 4.0;
    return final;
}

float myMap(vec3 p, float anim) {
    float nebNoise = abs(NebulaNoise(p / 0.5, anim) * 0.5) + 0.03;
    return nebNoise;
}

void main() {
    vec2 uv = fragmentTexCoord;
    vec2 coord = (uv - 0.5) * 2.0;
    coord.x *= resolution.x / resolution.y;

    vec2 screenSize = vec2(textureSize(SCREEN_TEXTURE, 0));
    vec2 normalizedSectionPos = vec2(section.x, section.y) / screenSize;
    vec2 normalizedSectionSize = vec2(section.z, section.w) / screenSize;
    vec2 screenUV = uv * normalizedSectionSize + vec2(
        normalizedSectionPos.x,
        1.0 - normalizedSectionPos.y - normalizedSectionSize.y
    );

    float baseTime = 10.0;
    float anim = time;

    vec3 world_pos = vec3(coord.x * 5.0, coord.y * 5.0, baseTime * 0.1);
    world_pos.xy += vec2(
        sin(anim * 0.35),
        cos(anim * 0.28 + 1.3)
    ) * 0.08;

    vec3 ray_dir = normalize(vec3(coord.x * 0.1, coord.y * 0.1, 1.0));

    vec4 sum = vec4(0.0);
    float d = 1.0;
    float t = 0.0;
    float td = 0.0;
    float min_dist = 0.0;
    float max_dist = 10.0;

    t = min_dist * step(t, min_dist);

    for (int i = 0; i < 20; i++) {
        vec3 pos = world_pos + t * ray_dir;

        if (td > 0.9 || d < 0.1 * t || t > 5.0 || sum.a > 0.99 || t > max_dist) break;

        d = myMap(pos, anim);
        d = max(d, 0.08);

        vec2 center_offset = (center - 0.5) * 2.0;
        center_offset.x *= resolution.x / resolution.y;
        vec3 star_center = vec3(center_offset, 0.0);
        vec3 ldst = star_center - pos;
        float lDist = max(length(ldst), 0.001);

        sum.rgb += (albedo.rgb / (lDist * lDist) / 30.0);
        sum.rgb *= 0.992 + 0.008 * sin(anim * 0.8);

        td += 1.0 / 50.0;
        d = max(d, 0.04);
        t += max(d * 0.1 * max(min(length(ldst), length(world_pos)), 1.0), 0.02);
    }

    vec3 nebulaColor = sum.rgb * t;
    float nebulaAlpha = clamp(nebulaColor.r + nebulaColor.g + nebulaColor.b, 0.0, 1.0);

    float radialMask = smoothstep(1.05, 0.18, length(coord));
    float pulse = 0.5 + 0.5 * sin(anim * 0.9 + coord.y * 3.0);
    vec2 distortion = vec2(
        sin(anim * 1.1 + coord.y * 6.0),
        cos(anim * 0.8 + coord.x * 5.0)
    ) * 0.0085;
    distortion += coord * (nebulaAlpha * 0.03 * radialMask);
    distortion *= 0.55 + 0.45 * pulse;

    vec4 refractedColor = texture(SCREEN_TEXTURE, clamp(screenUV + distortion, 0.0, 1.0));

    vec3 voidTint = mix(refractedColor.rgb, refractedColor.rgb * 0.18, radialMask * nebulaAlpha * 0.75);
    vec3 glowColor = voidTint + nebulaColor * (0.85 + radialMask * 0.35);
    float effectMask = clamp(radialMask * 0.7 + nebulaAlpha * 0.9, 0.0, 1.0);
    vec3 finalColor = mix(refractedColor.rgb, glowColor, clamp(nebulaAlpha * 0.85 + radialMask * 0.25, 0.0, 1.0));

    color = vec4(finalColor, effectMask);
}
