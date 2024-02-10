#version 330 core

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;

uniform float time;

uniform vec2 resolution;
uniform vec2 size;
uniform vec4 color;

uniform float angle = -0.2 * 3.141592;
uniform float position = 0;
uniform float spread = 0.3;
uniform float cutoff = 0.1; // side somehow
uniform float falloff = 0.2; // bottom fade
uniform float edge_fade = 0.3; // side fade
uniform float thickness = 300; // thickness

uniform float speed = 1.0;
uniform float ray1_density = 8.0;
uniform float ray2_density = 30.0;
uniform float ray2_intensity = 0.3;

uniform bool hdr = false;
uniform float seed = 5.0;

out vec4 COLOR;

// Random and noise functions from Book of Shader's chapter on Noise.
float random(vec2 _pygame_position)
{
    return fract(sin(dot(_pygame_position.xy,
                        vec2(12.9898, 78.233))) *
                 43758.5453123);
}

float noise(in vec2 pygame_position)
{
    vec2 i = floor(pygame_position);
    vec2 f = fract(pygame_position);

    // Four corners in 2D of a tile
    float a = random(i);
    float b = random(i + vec2(1.0, 0.0));
    float c = random(i + vec2(0.0, 1.0));
    float d = random(i + vec2(1.0, 1.0));

    // Smooth Interpolation

    // Cubic Hermine Curve. Same as SmoothStep()
    vec2 u = f * f * (3.0 - 2.0 * f);

    // Mix 4 coorners percentages
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

void main()
{
    float scale = size.x/size.y;
    // Rotate, skew and move the pygame_positions
    vec2 pixelCoord = vec2(fragmentTexCoord.x * resolution.x*scale , (1.0 - fragmentTexCoord.y) * resolution.y);

    vec2 transformed_pygame_position = (rotate(angle) * (pixelCoord - position)) / (thickness*(1-spread) + pixelCoord.y * spread);

    // Animate the ray according to the new transformed pygame_positions
    vec2 ray1 = vec2(transformed_pygame_position.x * ray1_density + sin(time * 0.1 * speed) * (ray1_density * 0.2) + seed, transformed_pygame_position.y);
    vec2 ray2 = vec2(transformed_pygame_position.x * ray2_density + sin(time * 0.2 * speed) * (ray1_density * 0.2) + seed, transformed_pygame_position.y);

    // Cut off the ray's edges
    float cut = step(cutoff, transformed_pygame_position.x) * step(cutoff, 1.0 - transformed_pygame_position.x);
    ray1 *= cut;
    ray2 *= cut;

    // Apply the noise pattern (i.e. create the rays)
    float rays;

    if (hdr)
    {
        rays = noise(ray1) + (noise(ray2) * ray2_intensity);
    }
    else
    {
        rays = clamp(noise(ray1) + (noise(ray2) * ray2_intensity), 0., 1.);
    }

    // Fade out edges
    rays *= smoothstep(0.0, falloff, 1 - pixelCoord.y / resolution.y);                // Bottom
    rays *= smoothstep(0.0 + cutoff, edge_fade + cutoff, transformed_pygame_position.x); // Left
    rays *= smoothstep(0.0 + cutoff, edge_fade + cutoff, 1.0 - transformed_pygame_position.x); // Right

    // Color to the rays
    vec3 shine = vec3(rays) * color.rgb;

    // Try different blending modes for a nicer effect. "Screen" is included in the code,
    // but take a look at https://godotshaders.com/snippet/blending-modes/ for more.
    // With "Screen" blend mode:
    shine = screen(texture(imageTexture, pixelCoord / resolution), vec4(color)).rgb;

    COLOR = vec4(shine, rays * color.a);
}
