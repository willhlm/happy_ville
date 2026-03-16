#version 330 core

uniform float u_time;
in vec2 fragmentTexCoord; // top-left is [0, 1] and bottom-right is [1, 0]

uniform int   beams = 5;
uniform float energy = 2.0;
uniform int   roughness = 5;
uniform int   frequency = 12;

uniform float speed = 1.2;
uniform float thickness = 0.01;
uniform float outline_thickness = 0.01;
uniform float beam_difference = 0.2;

uniform float progress = 1.0;
uniform float y_offset = 0.0;
uniform float fixed_edge_size = 0.06;
uniform vec2  noise_scale = vec2(1.0);
uniform int vertical = 1;
uniform vec3 shadow_color = vec3(0.005, 0.008, 0.005);
uniform vec3 core_color = vec3(0.08, 0.13, 0.07);
uniform vec3 glow_color = vec3(0.18, 0.26, 0.10);
uniform vec3 mist_color = vec3(0.015, 0.025, 0.015);

out vec4 color;

float hash(vec2 p) {
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453123);
}

float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);

    float a = hash(i);
    float b = hash(i + vec2(1.0, 0.0));
    float c = hash(i + vec2(0.0, 1.0));
    float d = hash(i + vec2(1.0, 1.0));

    vec2 u = f * f * (3.0 - 2.0 * f);

    return mix(a, b, u.x)
         + (c - a) * u.y * (1.0 - u.x)
         + (d - b) * u.x * u.y;
}

float fbm(vec2 uv) {
    float value = 0.0;
    float amp = 0.5;
    float freq = 1.0;

    for (int i = 0; i < 10; i++) {
        if (i >= roughness) break;
        value += amp * noise(uv * freq);
        freq *= 2.0;
        amp *= 0.5;
    }

    return value;
}

vec3 evilPalette(float core, float glow) {
    vec3 c = shadow_color;
    c += core_color * glow * 0.85;
    c += glow_color * core * 0.95;
    c += glow_color * pow(core, 3.0) * 0.18;
    return c;
}

vec4 beamLayer(vec2 uv, float idx) {
    float t = u_time * speed;
    float along = vertical == 1 ? uv.y : uv.x;
    float across = vertical == 1 ? uv.x : uv.y;
    float center_base = 0.5 + y_offset;

    float edgeLock =
        smoothstep(0.0, fixed_edge_size, along) *
        smoothstep(0.0, fixed_edge_size, 1.0 - along);

    float xSeed = idx * 7.13;

    // Noise along the beam axis that displaces the beam across the axis.
    float n = fbm(vec2(
        along * float(frequency) + xSeed,
        t + idx * 3.17
    ) * noise_scale);

    // center line of the beam
    float center =
        center_base
        + (n - 0.5) * 0.25 * energy * progress * edgeLock;

    // distance from current fragment to beam center
    float d = abs(across - center);

    float beamWidth = thickness * mix(1.0, 1.0 - beam_difference, clamp(idx / max(float(beams - 1), 1.0), 0.0, 1.0));
    float glowWidth = beamWidth + outline_thickness;

    float core = 1.0 - smoothstep(beamWidth, beamWidth + 0.01, d);
    float glow = 1.0 - smoothstep(glowWidth, glowWidth + 0.02, d);

    glow = max(glow - core, 0.0);

    // Slower, heavier pulsing reads more ominous than electrical flicker.
    float flicker = 0.92 + 0.08 * sin(u_time * 6.0 + idx * 4.1);
    float pulse = 0.84 + 0.16 * fbm(vec2(along * 6.0 + idx * 1.7, across * 3.0 - u_time * 0.35));
    float corruption = fbm(vec2(along * 18.0 + idx * 5.3, across * 9.0 + u_time * 0.18));
    corruption = smoothstep(0.38, 0.90, corruption);

    core *= flicker * pulse;
    glow *= flicker * (0.85 + corruption * 0.25);

    vec3 rgb = evilPalette(core, glow);
    rgb *= 0.90 + corruption * 0.12;
    float a = max(core, glow * 0.60);

    return vec4(rgb, a);
}

void main() {
    vec2 uv = fragmentTexCoord;

    vec4 result = vec4(0.0);

    for (int i = 0; i < 16; i++) {
        if (i >= beams) break;
        result = max(result, beamLayer(uv, float(i)));
    }

    // Low, dirty mist close to the band to keep it oppressive.
    float band_center = 0.5 + y_offset;
    float band_coord = vertical == 1 ? uv.x : uv.y;
    float band = 1.0 - smoothstep(0.0, 0.45, abs(band_coord - band_center));
    float mist = fbm(vec2((vertical == 1 ? uv.y : uv.x) * 3.0, (vertical == 1 ? uv.x : uv.y) * 2.0 + u_time * 0.08));
    vec3 mistCol = mist_color * mist * band * 0.07;

    vec2 p = uv * 2.0 - 1.0;
    float vignette = clamp(1.0 - dot(p, p) * 0.25, 0.0, 1.0);

    vec3 finalRgb = (result.rgb + mistCol) * vignette;
    float finalA = clamp(result.a, 0.0, 1.0);

    color = vec4(finalRgb, finalA);
}
