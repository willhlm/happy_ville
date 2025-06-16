#version 330 core

in vec2 fragmentTexCoord; // top-left is [0, 1] and bottom-right is [1, 0]
uniform float time;       // animate the smoke over time
uniform vec2 dir;         // direction vector for the smoke

out vec4 color;
uniform float speed = 0.3;

// Simple 2D noise function
float hash(vec2 p)
{
    return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

// Interpolated noise function
float noise(vec2 p)
{
    vec2 i = floor(p);
    vec2 f = fract(p);
    vec2 u = f * f * (3.0 - 2.0 * f);

    return mix(mix(hash(i + vec2(0.0, 0.0)), hash(i + vec2(1.0, 0.0)), u.x),
               mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
}

// Smooth smoke effect using layers of noise
float smokeEffect(vec2 uv, float time)
{
    float n = 0.1;
    float scale = 2.0;
    float persistence = 0.3;

    for (int i = 0; i < 4; i++)
    {
        n += noise(uv * scale + time * 0.1) * persistence;
        scale *= 2.0;
        persistence *= 0.5;
    }

    return n;
}

// Function to fade alpha near the edges of the texture
float edgeFade(vec2 uv)
{
    // Calculate distance to the nearest edge (smooth fade from 0.1 distance to edge)
    float fade = smoothstep(0.0, 0.2, uv.x) * smoothstep(0.0, 0.2, 1.0 - uv.x) *
                 smoothstep(0.0, 0.2, uv.y) * smoothstep(0.0, 0.2, 1.0 - uv.y);
    return fade;
}

void main()
{
    // Modify the texture coordinates to animate the smoke and make it move in the specified direction
    vec2 uv = fragmentTexCoord;
    uv -= vec2(dir.x, -dir.y) * time * speed; // Invert the Y-component of `dir`

    // Apply the smoke effect using noise
    float smoke = smokeEffect(uv * 2.0, time); // Adjust scale for effect

    // Alpha fade near edges
    float alphaFade = edgeFade(fragmentTexCoord); // Gradually fade at the edges

    // Control smoke intensity (clamp to 0-1 range)
    float smokeIntensity = clamp(smoke, 0.0, 1.0) * alphaFade; // Only apply smoke where intensity is high

    // Create the smoke color (white smoke, fading out at the edges)
    vec4 smokeColor = vec4(vec3(1.0), smokeIntensity * alphaFade); // Grayscale smoke color with transparency

    // Set final color with transparency for background
    // Use step to determine transparency based on smokeIntensity
    float visibility = step(0.01, smokeIntensity); // Step returns 1.0 if smokeIntensity > 0.01, else 0.0

    // Set the final color using the visibility factor (0 for transparent, 1 for visible smoke)
    color = smokeColor * visibility; // This will zero out the smoke color when visibility is 0
}
