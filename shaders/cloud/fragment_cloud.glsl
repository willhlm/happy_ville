#version 330 core

// Inputs
in vec2 fragmentTexCoord; // Texture coordinates for 2D space
out vec4 color;           // Final color output

// Uniform variables for configuration
uniform vec4 cloud_color = vec4(1); // Color of the clouds (including transparency)
uniform float cloud_opacity = 1; // Opacity of the clouds
uniform float time;        // Time variable for animation
uniform vec2 camera_scroll; // 
uniform vec2 u_resolution; 

// Function to interpolate (fade) used in Perlin noise
float fade(float t) {
    return t * t * t * (t * (t * 6.0 - 15.0) + 10.0);
}

// Function to generate a gradient
float grad(int hash, float x, float y) {
    int h = hash & 7; // Mask hash
    float u = h < 4 ? x : y;
    float v = h < 4 ? y : x;
    return ((h & 1) == 0 ? u : -u) + ((h & 2) == 0 ? v : -v);
}

// Function to generate Perlin noise
float perlin_noise(vec2 coord) {
    vec2 p = floor(coord);
    vec2 f = fract(coord);
    f = f * f * (3.0 - 2.0 * f);

    float n = p.x + p.y * 57.0;
    float res = mix(
        mix(grad(int(n + 0.0), f.x, f.y),
            grad(int(n + 1.0), f.x - 1.0, f.y), fade(f.x)),
        mix(grad(int(n + 57.0), f.x, f.y - 1.0),
            grad(int(n + 58.0), f.x - 1.0, f.y - 1.0), fade(f.x)),
        fade(f.y));
    return res;
}

// Function to generate layered Perlin noise for a cloud effect
float layered_perlin_noise(vec2 coord, float scale, float amplitude) {
    float noise = 0.0;
    float persistence = 0.5; // Influence of successive noise layers

    // Adding multiple layers of noise to create more complex effects
    for (int i = 0; i < 5; i++) {
        noise += perlin_noise(coord * scale) * amplitude;
        scale *= 2.0;
        amplitude *= persistence;
    }
    return noise;
}

void main() {
vec2 uv = fragmentTexCoord;
//uv.y = 1.0 - uv.y; // bottom = horizon

float perspective = pow(uv.y, 1); // warp for fake depth

float parallax_strength = mix(0.2, 1.0, perspective);

vec2 warped_uv = vec2(uv.x, perspective);

vec2 normalized_scroll = vec2(camera_scroll.x * perspective , 0 * camera_scroll.y) / u_resolution;

vec2 parallax_uv = warped_uv + normalized_scroll * parallax_strength;

float base_scale = mix(5, 0.7, perspective);

vec2 scroll_speed = vec2(0.0, 0.01);

float noise = 0;
for (int i = 0; i < 5; i++) {
    vec2 cloud_center = vec2(1);//vec2(fract(sin(float(i) * 0.1) * 43758.5453), fract(cos(float(i) * 0.1) * 43758.5453));    

    vec2 noise_uv = (parallax_uv * base_scale - time * scroll_speed ) * cloud_center;

    float noise1 = layered_perlin_noise(noise_uv, 1.0, 1.0);
    noise += noise1;// max(final_noise, noise);
}

float fade = smoothstep(0, 0.9, perspective); // fade near top/bottom
vec4 cloudColor = vec4(cloud_color.rgb, cloud_color.a * noise * cloud_opacity * fade);

color = cloudColor;


}