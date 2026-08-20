#version 330 core

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;

uniform float time;

uniform vec2 resolution; // game window size in pixels (your pixel grid)
uniform vec2 size;       // kept as-is (you already use it for aspect)
uniform vec4 color;

uniform float angle = -0.2;
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

// Pixelation size in logical game pixels. The game render is subsequently
// upscaled, so 1 preserves the native pixel-art grid; larger values make the
// rays intentionally chunkier.
uniform float pixelSizeScale = 1.0; // 1 = native pixels, 2 = 2x2 blocks, etc.


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

    // ---- God ray math (use snapped game coords) ----
    // The imaginary source sits on the render boundary opposite the travel
    // direction. Rotating `angle` therefore rotates source, rays, and their
    // fade together without requiring a per-object position.
    vec2 rayDirection = vec2(-sin(angle), cos(angle));
    vec2 centre = resolution * 0.5;
    vec2 distanceToSourceBoundary = vec2(1e20);
    if (rayDirection.x > 0.0) {
        distanceToSourceBoundary.x = centre.x / rayDirection.x;
    } else if (rayDirection.x < 0.0) {
        distanceToSourceBoundary.x = (resolution.x - centre.x) / -rayDirection.x;
    }
    if (rayDirection.y > 0.0) {
        distanceToSourceBoundary.y = centre.y / rayDirection.y;
    } else if (rayDirection.y < 0.0) {
        distanceToSourceBoundary.y = (resolution.y - centre.y) / -rayDirection.y;
    }
    float fictionalDistance = min(distanceToSourceBoundary.x, distanceToSourceBoundary.y);
    vec2 sourcePosition = centre - rayDirection * fictionalDistance;
    vec2 raySpace = rotate(angle) * (gameCoordPix - sourcePosition);
    vec2 transformed =
        // `angle` is supplied in radians (Tiled degrees are converted at spawn time).
        raySpace /
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

    // Fade from the source to the render boundary in the ray direction. At
    // 0° this is the original top-to-bottom fade; at 90° it fades right-to-left.
    vec2 distanceToBoundary = vec2(1e20);
    if (rayDirection.x > 0.0) {
        distanceToBoundary.x = (resolution.x - sourcePosition.x) / rayDirection.x;
    } else if (rayDirection.x < 0.0) {
        distanceToBoundary.x = -sourcePosition.x / rayDirection.x;
    }
    if (rayDirection.y > 0.0) {
        distanceToBoundary.y = (resolution.y - sourcePosition.y) / rayDirection.y;
    } else if (rayDirection.y < 0.0) {
        distanceToBoundary.y = -sourcePosition.y / rayDirection.y;
    }

    float rayLength = max(min(distanceToBoundary.x, distanceToBoundary.y), 1.0);
    float alongRay = raySpace.y;
    rays *= step(0.0, alongRay);
    rays *= smoothstep(0.0, falloff.y, 1.0 - (alongRay / rayLength));

    // Fade out the rays' cross-section (also in game-pixel space).
    rays *= smoothstep(0.0 + cutoff, edge_fade + cutoff, transformed.x);       // left edge
    rays *= smoothstep(0.0 + cutoff, edge_fade + cutoff, 1.0 - transformed.x); // right edge

    // Optional isotropic edge falloff in UV space (keeps it symmetrical)
    vec2 uv = fragmentTexCoord;
    float distToEdge = min(min(uv.x, 1.0 - uv.x), min(uv.y, 1.0 - uv.y));
    rays *= smoothstep(0.0, edge_falloff, distToEdge);

    // Keep the scene sample at its native game resolution; only the generated
    // ray pattern uses the coarser pixel grid.
    vec4 base = texture(imageTexture, fragmentTexCoord);
    vec3 out_rgb = screen(base, vec4(color)).rgb;

    COLOR = vec4(out_rgb, rays * color.a);
}
