#version 330 core

in vec2 fragmentTexCoord;
in vec2 worldPosition;

// Texture
uniform sampler2D imageTexture;

// Time
uniform float time;

// Wind parameters
uniform float wind_strength = 2.0;       // Overall wind intensity
uniform float wind_speed = 0.5;          // How fast the wind moves
uniform float wind_turbulence = 0.1;     // Randomness/gustiness
uniform vec2  wind_direction = vec2(1.0, 0.0); // wind direction (x,y)

// Sway parameters
uniform float branch_sway = 0.04;        // Large branch movement
uniform float leaf_flutter = 0.04;       // Small leaf flutter
uniform float sway_frequency = 1.0;      // Wave frequency for branches

// Rotation parameters
uniform float rotation_amount = 0.15;    // Leaf rotation (reduced for smoothness)

// Noise parameters
uniform float noise_scale = 0.001;       // Scale of noise pattern

// Anchor point (where movement = 0)
uniform vec2 anchor_point = vec2(0.5, 0.2);

out vec4 color;

// ----------------------
// Procedural noise (2D value noise + fbm)
// ----------------------
float hash12(vec2 p)
{
    // Deterministic hash -> [0,1)
    float h = dot(p, vec2(127.1, 311.7));
    return fract(sin(h) * 43758.5453123);
}

float valueNoise(vec2 p)
{
    vec2 i = floor(p);
    vec2 f = fract(p);

    // Smoothstep-like interpolation curve
    vec2 u = f * f * (3.0 - 2.0 * f);

    float a = hash12(i + vec2(0.0, 0.0));
    float b = hash12(i + vec2(1.0, 0.0));
    float c = hash12(i + vec2(0.0, 1.0));
    float d = hash12(i + vec2(1.0, 1.0));

    float x1 = mix(a, b, u.x);
    float x2 = mix(c, d, u.x);
    return mix(x1, x2, u.y); // [0,1)
}

float fbm(vec2 p)
{
    // 4 octaves is usually enough for “windy” turbulence
    float sum = 0.0;
    float amp = 0.55;
    float freq = 1.0;

    for (int i = 0; i < 4; i++)
    {
        sum += amp * valueNoise(p * freq);
        freq *= 2.0;
        amp *= 0.5;
    }
    return sum; // roughly [0,1)
}


void main()
{
    vec2 uv = fragmentTexCoord;

    // Normalize wind direction
    vec2 dir = wind_direction;
    float dirLen = length(dir);
    dir = (dirLen > 1e-6) ? (dir / dirLen) : vec2(1.0, 0.0);
    vec2 perp = vec2(-dir.y, dir.x);

    // Anchor falloff (biased radial)
    vec2 to_anchor = uv - anchor_point;
    to_anchor.x *= 0.6;
    float distance_from_anchor = length(to_anchor);
    float movement_strength = distance_from_anchor * distance_from_anchor;

    // ---------------------------------------
    // Noise fields (advected with wind)
    // ---------------------------------------
    // Large-scale gust field (slow, smooth)
    vec2 gust_p = worldPosition * (noise_scale * 0.6) + dir * (time * wind_speed * 0.03);
    float gust = fbm(gust_p);              // ~[0,1]
    float gust_signed = gust - 0.5;        // ~[-0.5,0.5]

    // Small-scale flutter field (faster, different scale)
    vec2 flut_p = worldPosition * (noise_scale * 2.5) + dir * (time * wind_speed * 0.12);
    float flut = fbm(flut_p);              // ~[0,1]
    float flut_signed = flut - 0.5;        // ~[-0.5,0.5]

    // A stable per-area seed so different leaf regions don’t sync
    // (Tune the 0.35 "cell size" to your worldPosition units)
    vec2 cell = floor(worldPosition * 0.35);
    float seedA = hash12(cell + vec2(11.0, 37.0));
    float seedB = hash12(cell + vec2(71.0, 19.0));

    // ---------------------------------------
    // Time signals with noise "time-warp"
    // ---------------------------------------
    float base_slow   = time * wind_speed * 0.30;
    float base_medium = time * wind_speed * 0.60;

    // Branch sway: add slow drifting phase so it won’t repeat cleanly
    float phase_drift = (fbm(vec2(base_slow * 0.05, seedA * 10.0)) - 0.5) * 2.5; // slow drift
    float sway_phase  = base_slow + phase_drift;

    // Also modulate branch amplitude by gusts (slow non-periodic variation)
    float gust_amp = 1.0 + gust_signed * 0.8; // ±40%ish

    // ---------------------------------------
    // Branch sway (still smooth, but less predictable)
    // ---------------------------------------
    float primary_sway = sin(sway_phase) * branch_sway;
    primary_sway += sin(sway_phase * 1.37 + (seedA * 6.2831853)) * branch_sway * 0.35;
    primary_sway *= gust_amp;

    // Secondary branch variation: use gust noise instead of a spatial sine wave
    float secondary_sway = gust_signed * branch_sway * 0.35;

    // ---------------------------------------
    // Leaf flutter (de-correlated from branch sway)
    // ---------------------------------------
    // Give each cell its own time-warp so flutter doesn’t move in unison.
    float local_time = base_medium
        + (seedA - 0.5) * 3.0
        + (fbm(vec2(base_medium * 0.12, seedB * 10.0)) - 0.5) * 2.0;

    // Noise-driven flutter (less sine = less “predictable loop”)
    float flutter = flut_signed * leaf_flutter * 1.2;

    // Add a tiny sinusoidal component but with per-cell phase so it’s not synchronized
    flutter += sin(local_time * 1.6 + seedB * 6.2831853) * leaf_flutter * 0.25;

    // Turbulence: keep it subtle
    float turbulence = flut_signed * wind_turbulence * 0.03;

    // ---------------------------------------
    // Combine into along-wind displacement
    // ---------------------------------------
    float along_wind = (primary_sway + secondary_sway + flutter + turbulence)
                       * movement_strength * wind_strength;

    // Perpendicular wiggle: use flutter noise (not uv waves)
    float cross_wind = (fbm(flut_p + perp * 3.1 + seedA * 5.0) - 0.5)
                       * branch_sway * 0.10
                       * movement_strength * wind_strength;

    vec2 displacement = dir * along_wind + perp * cross_wind;

    // Vertical bob: also noise-driven and de-correlated
    float vertical_bob = (fbm(gust_p + vec2(5.2, 1.7) + seedB * 3.0) - 0.5) * 0.018;
    float total_y_offset = vertical_bob * movement_strength * wind_strength;

    // Rotation: use flutter noise so it’s not locked to branch sway
    float rotation = flut_signed * rotation_amount * movement_strength * wind_strength * 0.5;

    // Apply rotation
    vec2 centered_uv = uv - vec2(0.5);
    float cos_rot = cos(rotation);
    float sin_rot = sin(rotation);

    vec2 rotated = vec2(
        centered_uv.x * cos_rot - centered_uv.y * sin_rot,
        centered_uv.x * sin_rot + centered_uv.y * cos_rot
    );
    vec2 rotated_uv = rotated + vec2(0.5);

    vec2 final_uv = rotated_uv + displacement + vec2(0.0, total_y_offset);
    color = texture(imageTexture, final_uv);
}
