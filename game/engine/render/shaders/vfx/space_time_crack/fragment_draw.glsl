#version 330 core

in vec2 fragmentTexCoord;

uniform sampler2D imageTexture;
uniform sampler2D SCREEN_TEXTURE;

uniform float time = 0.0;
uniform vec2 resolution = vec2(800.0, 600.0);
uniform vec4 section = vec4(0.0, 0.0, 800.0, 600.0);

uniform float crack_depth = 3.0;
uniform float crack_scale = 1.0;
uniform float crack_zebra_scale = 2.67;
uniform float crack_zebra_amp = 0;
uniform float crack_profile = 1.0;
uniform float crack_slope = 45.8;
uniform float crack_width = 0.001;

uniform vec2 refraction_offset = vec2(25.0, 25.0);
uniform vec2 reflection_offset = vec2(1.0, 1.0);
uniform vec4 reflection_color = vec4(0.588, 0.588, 0.588, 0.5);
uniform vec4 crack_color = vec4(0.0, 0.0, 0.0, 1.0);
uniform float field_strength = 0.1;
uniform float field_density = 2;
uniform float edge_fade = 0.12;

uniform float radial_fade_scale = 1.55;
uniform float radial_fade_inner = 0.18;
uniform float radial_field_inner = 0.22;

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

vec3 voronoiB(vec2 u) {
    vec2 p = floor(u);
    vec2 f = fract(u);
    float res = 8.0;
    vec2 cell = vec2(0.0);
    vec2 point = vec2(0.0);

    for (int j = -1; j <= 1; j++) {
        for (int i = -1; i <= 1; i++) {
            vec2 g = vec2(float(i), float(j));
            vec2 o = hash(p + g);
            vec2 r = g - f + o;
            float d = dot(r, r);
            if (d < res) {
                res = d;
                cell = g;
                point = r;
            }
        }
    }

    res = 8.0;
    for (int j = -2; j <= 2; j++) {
        for (int i = -2; i <= 2; i++) {
            vec2 g = cell + vec2(float(i), float(j));
            vec2 o = hash(p + g);
            vec2 r = g - f + o;
            if (dot(point - r, point - r) > 1e-5) {
                res = min(res, 0.5 * dot(point + r, normalize(r - point)));
            }
        }
    }

    return vec3(res, point + f);
}

float fbm(vec2 n) {
    float total = 0.0;
    float amp = 1.0;

    for (int i = 0; i < 7; i++) {
        total += noise(n) * amp;
        n += n;
        amp *= 0.5;
    }

    return total;
}

vec4 generateCracks(vec2 uv) {
    vec2 scaledUV = uv * crack_scale;
    vec4 crack = vec4(0.0);
    int layerCount = max(1, int(floor(crack_depth)));

    for (int i = 0; i < layerCount; i++) {
        vec2 zebra = vec2(crack_zebra_amp * fbm(scaledUV / crack_zebra_scale) * crack_zebra_scale);
        vec3 voronoi = voronoiB(scaledUV + zebra);
        float d = min(1.0, crack_slope * pow(max(0.0, voronoi.x - crack_width), crack_profile));
        crack += vec4(1.0 - d) / exp2(float(i));
        scaledUV *= 1.5;
    }

    crack *= crack_color;
    crack.a = clamp(crack.a, 0.0, 1.0);
    return crack;
}

void main() {
    vec2 uv = fragmentTexCoord;
    vec2 centered = uv - 0.5;
    vec2 aspectCoord = vec2(centered.x * (resolution.x / max(resolution.y, 1.0)), centered.y);
    vec2 screenSize = vec2(textureSize(SCREEN_TEXTURE, 0));
    vec2 normalizedSectionPos = vec2(section.x, section.y) / screenSize;
    vec2 normalizedSectionSize = vec2(section.z, section.w) / screenSize;
    vec2 sectionOrigin = vec2(
        normalizedSectionPos.x,
        1.0 - normalizedSectionPos.y - normalizedSectionSize.y
    );
    vec2 screenUV = uv * normalizedSectionSize + sectionOrigin;
    vec2 screenPixelSize = 1.0 / screenSize;
    vec2 localPixelSize = 1.0 / max(resolution, vec2(1.0));

    float edgeMaskX = smoothstep(0.0, edge_fade, uv.x) * (1.0 - smoothstep(1.0 - edge_fade, 1.0, uv.x));
    float edgeMaskY = smoothstep(0.0, edge_fade, uv.y) * (1.0 - smoothstep(1.0 - edge_fade, 1.0, uv.y));
    float edgeMask = edgeMaskX * edgeMaskY;
    float radialDistance = length(aspectCoord) * radial_fade_scale;
    float centerMask = smoothstep(1.0, radial_fade_inner, radialDistance);
    float softenedEdgeMask = edgeMask * centerMask * centerMask;

    vec4 crack = generateCracks(uv);
    vec4 adjacentCrack = generateCracks(clamp(uv + localPixelSize * reflection_offset, 0.0, 1.0));
    crack.a *= softenedEdgeMask;
    adjacentCrack.a *= softenedEdgeMask;
    float crackMask = clamp(crack.a, 0.0, 1.0);

    float radial = smoothstep(1.0, radial_field_inner, radialDistance);
    float fieldMask = max(softenedEdgeMask * 0.65, radial * 0.35);

    vec2 noiseUV = uv * field_density;
    float flowA = fbm(noiseUV + vec2(time * 0.55, -time * 0.35));
    float flowB = fbm(noiseUV.yx * 1.17 + vec2(-time * 0.4, time * 0.6));
    float flowC = fbm((uv + vec2(flowA, flowB) * 0.08) * (field_density * 0.7) + time * 0.25);

    vec2 dir = length(aspectCoord) > 0.0001 ? normalize(aspectCoord) : vec2(0.0, 0.0);
    vec2 tangent = vec2(-dir.y, dir.x);
    vec2 fieldWarp = vec2(flowA - 0.5, flowB - 0.5) * field_strength;
    fieldWarp += tangent * ((flowC - 0.5) * field_strength * 1.6);
    fieldWarp += dir * (sin(time * 1.2 + flowA * 6.2831) * field_strength * 0.8);
    fieldWarp *= fieldMask * 0.7;

    if (adjacentCrack.a >= 1.0) {
        color = reflection_color;
        return;
    }

    vec2 crackWarp = crackMask * (screenPixelSize * refraction_offset);
    vec2 refractedUV = clamp(screenUV + fieldWarp + crackWarp, 0.0, 1.0);
    vec4 refracted = texture(SCREEN_TEXTURE, refractedUV);

    vec3 crackGlow = mix(vec3(0.42, 0.62, 0.95), vec3(0.95, 0.98, 1.0), flowA);
    vec3 finalRgb = refracted.rgb + crackGlow * crackMask * 0.22;
    float alpha = clamp(max(fieldMask * 0.85, crackMask), 0.0, 1.0);
    color = vec4(finalRgb, alpha);
}
