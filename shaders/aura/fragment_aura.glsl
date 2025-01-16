#version 330 core

in vec2 fragmentTexCoord; // Texture coordinates
uniform sampler2D imageTexture; // Silhouette texture

uniform vec3 auraColorStart = vec3(0.0, 1.0, 1.0); // Start color of aura gradient (cyan)
uniform vec3 auraColorEnd = vec3(0.0, 0.0, 1.0);   // End color of aura gradient (blue)
uniform float time;          // Time for animation
uniform float auraSpeed = 1.0;  // Speed of aura animation
uniform float auraScale = 8.0;  // Scale of the aura noise
uniform float auraThickness = 0.1; // Thickness of the aura effect
uniform float glowIntensity = 2.0; // Intensity of the aura glow

out vec4 color;

// Random number generator
float rand(vec2 co) {
    return fract(sin(dot(co.xy, vec2(12.9898, 78.233))) * 43758.5453);
}

// Noise function
float noise(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    f = f * f * (3.0 - 2.0 * f);
    float n = i.x + i.y * 57.0;
    return mix(
        mix(rand(vec2(n, n + 1.0)), rand(vec2(n + 1.0, n + 2.0)), f.x),
        mix(rand(vec2(n + 57.0, n + 58.0)), rand(vec2(n + 58.0, n + 59.0)), f.x),
        f.y
    );
}

// Fractal Brownian Motion (FBM) for layered noise
float fbm(vec2 p) {
    float f = 0.0;
    mat2 m = mat2(vec2(1.6, 1.2), vec2(-1.2, 1.6));
    f += 0.5000 * noise(p); p = m * p;
    f += 0.2500 * noise(p); p = m * p;
    f += 0.1250 * noise(p); p = m * p;
    f += 0.0625 * noise(p); p = m * p;
    return f;
}

void main() {
    // Sample the silhouette texture
    vec4 silhouette = texture(imageTexture, fragmentTexCoord);

    // Aura effect calculation
    float distance = 1.0 - silhouette.a; // Determine distance from the edge
    if (distance > 0.0 && distance <= auraThickness) {
        // Calculate dynamic noise
        vec2 uv = fragmentTexCoord * auraScale + vec2(time * auraSpeed, time * auraSpeed);
        float auraNoise = fbm(uv);

        // Gradient interpolation for aura color
        float gradientFactor = distance / auraThickness;
        vec3 auraColor = mix(auraColorStart, auraColorEnd, gradientFactor);

        // Final aura color with noise-based intensity
        float auraAlpha = pow(gradientFactor, glowIntensity) * auraNoise;
        color = vec4(auraColor, auraAlpha);
    } else if (silhouette.a > 0.0) {
        // Render the silhouette intact
        color = silhouette;
    } else {
        // Transparent background
        color = vec4(0.0);
    }
}
