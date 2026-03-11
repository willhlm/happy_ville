#version 330 core

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;

uniform float time;

uniform vec2 resolution;
uniform vec2 size;
uniform vec4 color;

// Changed: center position for radial rays (in normalized coordinates 0-1)
uniform vec2 center = vec2(0.5, 0.5);
uniform float max_distance = 1.0; // Maximum distance for rays
uniform float min_distance = 0.1; // Minimum distance (creates a "hole" in center)

uniform float spread = 0.3;
uniform float cutoff = 0.1;
uniform float edge_fade = 0.3;
uniform float thickness = 300;

uniform float speed = 1.0;
uniform float ray1_density = 8.0;
uniform float ray2_density = 30.0;
uniform float ray2_intensity = 0.3;

// New: Controls for radial behavior
uniform float angular_frequency = 12.0; // How many "rays" around the circle
uniform float radial_frequency = 4.0;   // Frequency along each ray
uniform float rotation_speed = 0.1;     // How fast the pattern rotates

// Enhanced animation controls
uniform float flow_speed = 0.5;         // Speed of rays flowing outward
uniform float pulse_speed = 0.8;        // Speed of pulsing effect
uniform float pulse_strength = 0.3;     // Strength of pulsing
uniform float turbulence_speed = 0.2;   // Speed of turbulence
uniform float turbulence_strength = 0.4; // Strength of turbulence

// Edge falloff controls
uniform float edge_falloff_distance = 0.3; // Distance from edge where falloff starts (0.0-0.5)
uniform bool circular_falloff = false;       // Use circular falloff instead of rectangular

uniform bool hdr = false;
uniform float seed = 5.0;

out vec4 COLOR;

// Random and noise functions
float random(vec2 _position)
{
    return fract(sin(dot(_position.xy,
                        vec2(12.9898, 78.233))) *
                 43758.5453123);
}

float noise(in vec2 position)
{
    vec2 i = floor(position);
    vec2 f = fract(position);

    float a = random(i);
    float b = random(i + vec2(1.0, 0.0));
    float c = random(i + vec2(0.0, 1.0));
    float d = random(i + vec2(1.0, 1.0));

    vec2 u = f * f * (3.0 - 2.0 * f);

    return mix(a, b, u.x) +
           (c - a) * u.y * (1.0 - u.x) +
           (d - b) * u.x * u.y;
}

vec4 screen(vec4 base, vec4 blend)
{
    return 1.0 - (1.0 - base) * (1.0 - blend);
}

void main()
{
    float scale = size.x/size.y;
    vec2 pixelCoord = vec2(fragmentTexCoord.x * resolution.x * scale, 
                          (1.0 - fragmentTexCoord.y) * resolution.y);
    
    // Convert to normalized coordinates
    vec2 uv = pixelCoord / resolution;
    
    // Calculate distance and angle from center
    vec2 toCenter = uv - center;
    float distance = length(toCenter);
    float angle = atan(toCenter.y, toCenter.x);
    
    // Normalize distance (0 = center, 1 = edge)
    float normalizedDistance = distance / max_distance;
    
    // Enhanced animation system
    float baseTime = time * speed;
    
    // Flowing animation - rays move outward from center
    float flowOffset = baseTime * flow_speed;
    
    // Pulsing animation - intensity varies over time
    float pulsePhase = sin(baseTime * pulse_speed) * pulse_strength;
    
    // Turbulence - adds organic movement to the rays
    float turbulence1 = sin(baseTime * turbulence_speed + angle * 3.0) * turbulence_strength;
    float turbulence2 = cos(baseTime * turbulence_speed * 1.3 + angle * 2.0) * turbulence_strength * 0.7;
    
    // Rotation with slight variation
    float rotationOffset = time * rotation_speed + sin(time * 0.1) * 0.1;
    
    // Create radial coordinate system with enhanced animation
    vec2 radialCoord = vec2(
        angle + rotationOffset, 
        normalizedDistance - flowOffset // Subtract to make rays flow outward
    );
    
    // Apply ray density with multiple animation layers
    vec2 ray1 = vec2(
        radialCoord.x * angular_frequency + turbulence1 + seed,
        radialCoord.y * radial_frequency + flowOffset * 0.5
    );
    
    vec2 ray2 = vec2(
        radialCoord.x * angular_frequency * 1.3 + turbulence2 + seed + 1.0,
        radialCoord.y * radial_frequency * 1.1 + flowOffset * 0.3
    );
    
    // Distance-based cutoff (creates the "hole" in center and fades at edges)
    float distanceCutoff = smoothstep(min_distance, min_distance + cutoff, normalizedDistance) *
                          smoothstep(max_distance, max_distance - edge_fade, normalizedDistance);
    
    // Apply the noise pattern with pulsing
    float baseRays;
    if (hdr)
    {
        baseRays = noise(ray1) + (noise(ray2) * ray2_intensity);
    }
    else
    {
        baseRays = clamp(noise(ray1) + (noise(ray2) * ray2_intensity), 0., 1.);
    }
    
    // Add pulsing effect
    float rays = baseRays * (1.0 + pulsePhase);
    
    // Apply distance-based fading
    rays *= distanceCutoff;
    
    // Enhanced radial falloff with breathing effect
    float breathingFalloff = smoothstep(max_distance, max_distance * (0.7 + pulsePhase * 0.1), normalizedDistance);
    rays *= breathingFalloff;
    
    // Enhanced angular variation with slow movement
    float angularShift = time * 0.05; // Slow shift in angular pattern
    float angularVariation = (sin(angle * angular_frequency * 0.5 + angularShift) * 0.5 + 0.5) * 0.4 + 0.6;
    rays *= angularVariation;
    
    // Add some flickering for more organic feel
    float flicker = 0.95 + 0.05 * sin(time * 8.0 + angle * 10.0);
    rays *= flicker;
    
    // Edge falloff to prevent hard texture boundaries
    float edgeFade = 1.0;
    
    if (circular_falloff) {
        // Circular falloff - creates a soft circular vignette
        float distanceFromCenter = length(uv - vec2(0.5, 0.5));
        float maxRadius = 0.5; // Half the texture (circle inscribed in square)
        float fadeStart = maxRadius - edge_falloff_distance;
        edgeFade = 1.0 - smoothstep(fadeStart, maxRadius, distanceFromCenter);
    } else {
        // Rectangular falloff - fades towards all four edges
        float fadeLeft = smoothstep(0.0, edge_falloff_distance, uv.x);
        float fadeRight = smoothstep(0.0, edge_falloff_distance, 1.0 - uv.x);
        float fadeBottom = smoothstep(0.0, edge_falloff_distance, uv.y);
        float fadeTop = smoothstep(0.0, edge_falloff_distance, 1.0 - uv.y);
        edgeFade = fadeLeft * fadeRight * fadeBottom * fadeTop;
    }
    
    // Apply edge falloff
    rays *= edgeFade;
    
    // Color the rays
    vec3 shine = vec3(rays) * color.rgb;
    
    // Blend with original texture
    vec4 originalColor = texture(imageTexture, uv);
    shine = screen(originalColor, vec4(shine, rays)).rgb;
    
    COLOR = vec4(shine, rays * color.a);
}