#version 330 core

// Inputs
in vec2 fragmentTexCoord; // Texture coordinates for 2D space
out vec4 color;           // Final color output

// Uniform variables for configuration
uniform vec4 cloud_color = vec4(1); // Color of the clouds (including transparency)
uniform float cloud_opacity = 0.7; // Opacity of the clouds
uniform float time;        // Time variable for animation

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
    // Get the UV coordinates (texture coordinates)
    vec2 uv = fragmentTexCoord;

    // Add animation to the UV coordinates
    float speed = 0.01; // Speed of cloud movement
    vec2 animated_uv = uv + vec2(time * speed, time * speed);

    // Parameters for cloud generation
    int num_clouds = 20; // Number of clouds
    float cloud_size = 1; // Small cloud size
    float scale = 2.0; // Reduced scale of noise

    // Initialize the final noise result
    float final_noise = 0.0;

    for (int i = 0; i < num_clouds; i++) {
        // Random offset for each cloud
        float random_offset = float(i) * 0.01;
        vec2 cloud_center = vec2(fract(sin(float(i) * 0.1) * 43758.5453), fract(cos(float(i) * 0.1) * 43758.5453));

        // Modify the UV coordinates for cloud noise effect
        vec2 cloud_uv = (animated_uv - cloud_center) * (scale * cloud_size);
        float noise = layered_perlin_noise(cloud_uv, 1, 1.0);

        // Smooth and clamp the noise value
        noise = smoothstep(0.3, 0.7, noise);
        final_noise = max(final_noise, noise);
    }

    // Set the cloud color based on the uniform
    vec4 cloudColor = vec4(cloud_color.rgb, cloud_color.a * final_noise * cloud_opacity);

    // Output the final color
    color = cloudColor;
}
