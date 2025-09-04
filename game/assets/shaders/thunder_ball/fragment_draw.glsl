#version 330 core

in vec2 fragmentTexCoord; // top-left is [0,1], bottom-right is [1,0]
out vec4 color;

uniform float iTime;            // Time in seconds
uniform vec2 iResolution;       // Viewport resolution (e.g., screen size)

// --- Constants & Helpers ---
#define TAU 6.28318530718

mat2 Rotate(float angle) {
    return mat2(cos(angle), sin(angle), -sin(angle), cos(angle));
}

float RandomFloat(vec2 seed) {
    seed = sin(seed * vec2(123.45, 546.23)) * 345.21 + 12.57;
    return fract(seed.x * seed.y);
}

float SimpleNoise(vec2 uv, float octaves) {
    float sn = 0.0;
    float amplitude = 1.0;
    float deno = 0.0;
    octaves = clamp(octaves, 1.0, 6.0);
    for (float i = 1.0; i <= octaves; i++) {
        vec2 grid = smoothstep(0.0, 1.0, fract(uv));
        vec2 id = floor(uv);
        vec2 offs = vec2(0.0, 1.0);
        float bl = RandomFloat(id);
        float br = RandomFloat(id + offs.yx);
        float tl = RandomFloat(id + offs);
        float tr = RandomFloat(id + offs.yy);
        sn += mix(mix(bl, br, grid.x), mix(tl, tr, grid.x), grid.y) * amplitude;
        deno += amplitude;
        uv *= 3.5;
        amplitude *= 0.5;
    }
    return sn / deno;
}

float CircleSDF(vec2 p, float r) {
    return length(p) - r;
}

float LineSDF(vec2 p, vec2 a, vec2 b, float s) {
    vec2 pa = a - p;
    vec2 ba = a - b;
    float h = clamp(dot(pa, ba) / dot(ba, ba), 0.0, 1.0);
    return length(pa - ba * h) - s;
}

vec3 Bolt(vec2 uv, float len, float ind) {
    vec2 t = vec2(0.0, mod(iTime, 200.0) * 2.0);

    float sn = SimpleNoise(uv * 20.0 - t * 3.0 + vec2(ind * 1.5, 0.0), 2.0) * 2.0 - 1.0;
    uv.x += sn * 0.03 * smoothstep(0.0, 0.2, abs(uv.y));

    vec3 l = vec3(LineSDF(uv, vec2(0.0), vec2(0.0, len), 0.0001));
    l = 0.1 / max(vec3(0.0), l) * vec3(0.1, 0.2, 0.6);
    l = clamp(1.0 - exp(l * -0.02), 0.0, 1.0) * smoothstep(len - 0.01, 0.0, abs(uv.y));
    vec3 bolt = l;

    uv = Rotate(TAU * 0.125) * uv;
    sn = SimpleNoise(uv * 25.0 - t * 4.0 + vec2(ind * 2.3, 0.0), 2.0) * 2.0 - 1.0;
    uv.x += sn * uv.y * 0.8 * smoothstep(0.1, 0.25, len);
    len *= 0.5;
    l = vec3(LineSDF(uv, vec2(0.0), vec2(0.0, len), -1e-3));
    l = 0.2 / max(vec3(0.0), l) * vec3(0.1, 0.2, 0.6);
    l = clamp(1.0 - exp(l * -0.03), 0.0, 1.0) * smoothstep(len * 0.7, 0.0, abs(uv.y));
    bolt += l;

    float hz = 4.0;
    hz *= iTime * TAU;
    float r = RandomFloat(vec2(ind)) * 0.5 * TAU;
    float flicker = sin(hz + r) * 0.5 + 0.5;
    return bolt * smoothstep(0.5, 0.0, flicker);
}

// --- Main ---
void main()
{
    // Reconstruct UV coords in screen space (-aspect to +aspect)
    vec2 uv = (fragmentTexCoord * vec2(iResolution.x, iResolution.y) - 0.5 * iResolution.xy) / iResolution.y;
    uv *= 0.4;

    vec3 col = vec3(0.0);

    // Core lightning pulse
    float r = 0.02 * SimpleNoise(uv * 50.0 - vec2(0.0, mod(iTime, 200.0) * 5.0), 3.0);
    vec3 core = 0.6 / max(0.0, CircleSDF(uv, r)) * vec3(0.1, 0.1, 0.5);
    core = 1.0 - exp(core * -0.05);
    col = core;

    // Lightning bolts
    float boltCount = floor(RandomFloat(vec2(floor(iTime / 0.2))) * 2.0 + 3.5);
    for (float i = 0.0; i < 8.0; i++) { // loop always 8 times, only use when i < boltCount
        if (i >= boltCount) break;
        float angle = i * TAU / boltCount;
        angle += RandomFloat(vec2(boltCount + floor(iTime * 5.0 + i))) * 0.5;
        col += Bolt(Rotate(angle) * uv, 0.1 * RandomFloat(vec2(angle)) * 0.5 + 0.2, i);
    }

float alpha = max(max(col.r, col.g), col.b); // strongest channel as alpha
color = vec4(col, alpha);

}
