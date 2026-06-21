#version 330 core

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;
out vec4 COLOR;

uniform float TIME;
uniform vec4 wave_color = vec4(1.0);

uniform float speed = 2.0;
uniform float frequency = 6.0;
uniform float width = 0.05;
uniform float fade = 0.7;
uniform float radial_fade_power = 1.0;

uniform vec2 center = vec2(0.5, 0.5);
uniform vec2 resolution = vec2(140.0, 140.0);
uniform float reference_size = 140.0;

uniform float sine_scale = 10.0;
uniform float sine_speed = 1.0;
uniform float sine_strength = 0.04;

uniform float noise_scale = 2.0;
uniform float noise_strength = 0.015;

uniform float noise_speed = 0.05;

// Emission control:
// Set emit = 0.0 to stop spawning new waves (existing waves keep travelling).
// When setting emit to 0.0, also set emit_stop_time = TIME so the shader knows
// exactly when emission was halted.
uniform float emit = 1.0;
uniform float emit_stop_time = 0.0;

const int MAX_PULSES = 12;

float hash12(vec2 p) {
    vec3 p3 = fract(vec3(p.xyx) * 0.1031);
    p3 += dot(p3, p3.yzx + 33.33);
    return fract((p3.x + p3.y) * p3.z);
}

float value_noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);

    // Smooth interpolation curve.
    f = f * f * (3.0 - 2.0 * f);

    float a = hash12(i + vec2(0.0, 0.0));
    float b = hash12(i + vec2(1.0, 0.0));
    float c = hash12(i + vec2(0.0, 1.0));
    float d = hash12(i + vec2(1.0, 1.0));

    return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

float fbm_noise(vec2 p) {
    float total = 0.0;
    float amplitude = 0.5;
    float amplitude_sum = 0.0;

    mat2 rot = mat2(
        0.80, -0.60,
        0.60,  0.80
    );

    for (int i = 0; i < 4; i++) {
        total += value_noise(p) * amplitude;
        amplitude_sum += amplitude;
        p = rot * p * 2.02 + vec2(19.17, 7.31);
        amplitude *= 0.5;
    }

    return total / max(amplitude_sum, 0.0001);
}


void main() {
    vec2 centered_uv = fragmentTexCoord - center;
    vec2 centered_px = centered_uv * resolution;

    float dist = length(centered_px) / max(reference_size, 1.0);
    float angle = atan(centered_px.y, centered_px.x);

    float sine_distortion =
        sin(angle * sine_scale + TIME * sine_speed) +
        0.5 * sin(angle * sine_scale * 2.3 - TIME * sine_speed * 1.7);

    vec2 polar_uv = vec2(
        angle / 6.2831853,
        dist
    );

    polar_uv += vec2(0.0, TIME * noise_speed);

    float noise = fbm_noise(polar_uv * noise_scale);

    noise = noise * 2.0 - 1.0;

     float distortion =
        sine_distortion * sine_strength +
        noise * noise_strength;

    dist += distortion;

    vec2 max_extent_px = max(center * resolution, (1.0 - center) * resolution);
    float max_dist = length(max_extent_px) / max(reference_size, 1.0);

    // emission_front is frozen when emit=0, controlling how many pulses exist and
    // their birth positions. wave_front always advances with TIME so pulses keep moving.
    float emission_time = mix(emit_stop_time, TIME, clamp(emit, 0.0, 1.0));

    float wave_front = TIME * speed;
    float emission_front = emission_time * speed;
    float pulse_spacing = max(width * 1.5, 1.0 / max(frequency, 1.0));
    int emitted_count = min(MAX_PULSES, int(floor(emission_front / pulse_spacing)) + 1);

    // How far each pulse has travelled beyond its frozen birth position.
    float travel = wave_front - emission_front;
    float lead_front = mod(emission_front, pulse_spacing);
    float ring = 0.0;

    for (int i = 0; i < MAX_PULSES; i++) {
        if (i >= emitted_count) {
            continue;
        }
        // Birth position + travel keeps the ring moving after emission stops.
        float pulse_front = lead_front + float(i) * pulse_spacing + travel;
        if (pulse_front > max_dist + width) {
            continue;
        }

        float pulse_ring = smoothstep(pulse_front - width, pulse_front, dist) *
                           (1.0 - smoothstep(pulse_front, pulse_front + width, dist));
        ring = clamp(ring + pulse_ring, 0.0, 1.0);
    }
    float fade_radius = max(max_dist * fade, 0.0001);
    float radial_alpha = clamp(1.0 - (dist / fade_radius), 0.0, 1.0);
    radial_alpha = pow(radial_alpha, max(radial_fade_power, 0.001));

    float alpha = ring * radial_alpha;


    COLOR = vec4(wave_color.rgb, alpha);
}
