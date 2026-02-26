#version 330 core

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;

uniform float time;

uniform vec2 resolution; // game window size in pixels (your pixel grid)
uniform vec2 size;       // kept as-is (you already use it for aspect)
uniform vec4 color;

uniform float angle = -0.2;
uniform vec2 position = vec2(0,0);
uniform vec2 falloff = vec2(0,0.3);

uniform float spread = 0.3;
uniform float cutoff = 0.1;
uniform float edge_fade = 0.3;
uniform float thickness = 300.0;

uniform float edge_falloff = 0.0;

uniform float speed = 1.0;
uniform float ray1_density = 8.0;
uniform float ray2_density = 30.0;
uniform float ray2_intensity = 0.3;

uniform bool hdr = false;
uniform float seed = 5.0;

// NEW: pixelation size in *game pixels*
uniform float pixelSizeScale = 1; // 1 = native pixels, 2 = 2x2 blocks, etc.


out vec4 COLOR;

// Random and noise functions
float random(vec2 _pygame_position)
{
    return fract(sin(dot(_pygame_position.xy, vec2(12.9898, 78.233))) * 43758.5453123);
}

float noise(in vec2 pygame_position)
{
    vec2 i = floor(pygame_position);
    vec2 f = fract(pygame_position);

    float a = random(i);
    float b = random(i + vec2(1.0, 0.0));
    float c = random(i + vec2(0.0, 1.0));
    float d = random(i + vec2(1.0, 1.0));

    vec2 u = f * f * (3.0 - 2.0 * f);

    return mix(a, b, u.x) +
           (c - a) * u.y * (1.0 - u.x) +
           (d - b) * u.x * u.y;
}

mat2 rotate(float _angle)
{
    return mat2(vec2(cos(_angle), -sin(_angle)),
                vec2(sin(_angle), cos(_angle)));
}

vec4 screen(vec4 base, vec4 blend)
{
    return 1.0 - (1.0 - base) * (1.0 - blend);
}

// Snap a coordinate (in game pixels) to a pixel grid of size `stepPx`.
// Snap a coordinate (in game pixels) to a pixel grid of size `stepPx`.
vec2 pixel_snap(vec2 p, float stepPx)
{
    stepPx = max(stepPx, 1.0);
    return floor(p / stepPx) * stepPx;
}

void main()
{
    // 1) Convert fragment UV to *game pixel space* (stable regardless of render texture size)
    vec2 gameCoord = vec2(
        fragmentTexCoord.x * resolution.x,
        (1.0 - fragmentTexCoord.y) * resolution.y
    );

    // 2) Snap to your pixel grid (same pixel size as the game)
    vec2 gameCoordPix = pixel_snap(gameCoord, pixelSizeScale);

    // 3) Convert snapped gameCoord back to UV for sampling
    //    This guarantees UV stays in [0..1] as long as fragmentTexCoord was in [0..1].
    vec2 snappedUV = vec2(
        gameCoordPix.x / resolution.x,
        1.0 - (gameCoordPix.y / resolution.y)
    );

    // Extra safety (prevents any edge-case sampling outside)
    snappedUV = clamp(snappedUV, vec2(0.0), vec2(1.0));

    // ---- God ray math (use snapped game coords) ----
    vec2 transformed =
        (rotate(angle * 3.141592) * (gameCoordPix - position)) /
        (thickness * (1.0 - spread) + gameCoordPix.y * spread);

    vec2 ray1 = vec2(
        transformed.x * ray1_density +
        sin(time * 0.1 * speed) * (ray1_density * 0.2) + seed,
        transformed.y
    );

    vec2 ray2 = vec2(
        transformed.x * ray2_density +
        sin(time * 0.2 * speed) * (ray1_density * 0.2) + seed,
        transformed.y
    );

    float cut = step(cutoff, transformed.x) * step(cutoff, 1.0 - transformed.x);
    ray1 *= cut;
    ray2 *= cut;

    float rays;
    if (hdr) {
        rays = noise(ray1) + (noise(ray2) * ray2_intensity);
    } else {
        rays = clamp(noise(ray1) + (noise(ray2) * ray2_intensity), 0.0, 1.0);
    }

    // Fade out edges (also in game-pixel space)
    rays *= smoothstep(0.0, falloff.y, 1.0 - (gameCoordPix.y / resolution.y)); // bottom fade
    rays *= smoothstep(0.0 + cutoff, edge_fade + cutoff, transformed.x);       // left edge
    rays *= smoothstep(0.0 + cutoff, edge_fade + cutoff, 1.0 - transformed.x); // right edge

    // Optional isotropic edge falloff in UV space (keeps it symmetrical)
    vec2 uv = fragmentTexCoord;
    float distToEdge = min(min(uv.x, 1.0 - uv.x), min(uv.y, 1.0 - uv.y));
    rays *= smoothstep(0.0, edge_falloff, distToEdge);

    // ---- Blend with scene using snapped UV ----
    vec4 base = texture(imageTexture, snappedUV);
    vec3 out_rgb = screen(base, vec4(color)).rgb;

    COLOR = vec4(out_rgb, rays * color.a);
}