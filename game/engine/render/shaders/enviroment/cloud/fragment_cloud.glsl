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

// Simple random function
float random(vec2 st) {
    return fract(sin(dot(st.xy, vec2(12.9898, 78.233))) * 43758.5453123);
}

// Value noise
float noise(vec2 st) {
    vec2 i = floor(st);
    vec2 f = fract(st);

    // Four corners
    float a = random(i);
    float b = random(i + vec2(1.0, 0.0));
    float c = random(i + vec2(0.0, 1.0));
    float d = random(i + vec2(1.0, 1.0));

    // Smooth interpolation
    vec2 u = f * f * (3.0 - 2.0 * f);

    return mix(a, b, u.x) +
            (c - a) * u.y * (1.0 - u.x) +
            (d - b) * u.x * u.y;
}

// Fractal Brownian Motion
float fbm(vec2 st) {
    float value = 0.0;
    float amplitude = 0.5;
    float frequency = 1.0;
    
    for (int i = 0; i < 5; i++) {
        value += amplitude * noise(st * frequency);
        frequency *= 2.0;
        amplitude *= 0.5;
    }
    return value;
}

void main() {
    vec2 uv = fragmentTexCoord;        
    // Gentler perspective that doesn't create extreme distortion
    // Now perspective is small at top (horizon) and large at bottom (close)
    float perspective = mix(0.3, 1.0, pow(uv.y, 1.2));
    
    float parallax_strength = mix(0.3, 1.0, uv.y);
    
    vec2 normalized_scroll = vec2(camera_scroll.x * parallax_strength, 0 * camera_scroll.y) / u_resolution;
    
    vec2 parallax_uv = uv + normalized_scroll * parallax_strength;
    
    // More moderate scale range to avoid extreme stretching
    float base_scale = mix(2.0, 1.0, pow(uv.y, 0.8));
    
    // CHANGED: Clouds move toward horizon (positive Y direction after flip = toward top of screen)
    vec2 scroll_speed = vec2(0.0, 0.01); // Negative to move "up" in flipped coords = into depth
    
    // Gentler perspective scaling to avoid distortion
    float y_stretch = mix(1.5, 1.0, pow(uv.y, 0.5));
    vec2 perspective_scale = vec2(base_scale, base_scale * y_stretch * 4);
    
    vec2 noise_uv = (parallax_uv * perspective_scale - time * scroll_speed);
    noise_uv += vec2(100.789, 200.456);
    
    // Use fbm for cloud generation
    float noise_value = fbm(noise_uv * 2.5);
    
    // Better cloud shaping
    float cloud_threshold = 0.5;
    float cloud_softness = 0.2;
    
    float cloud_alpha = smoothstep(cloud_threshold - cloud_softness, 
                                   cloud_threshold + cloud_softness, 
                                   noise_value);
    
    // Make clouds more defined
    cloud_alpha = pow(cloud_alpha, 1.2);
    
    // Fade at top and bottom edges
    float fade_top = smoothstep(0.0, 0.15, uv.y);
    float fade_bottom = smoothstep(1.0, 0.85, uv.y);
    float fade = fade_top * fade_bottom;
    
    vec4 cloudColor = vec4(cloud_color.rgb, cloud_color.a * cloud_alpha * cloud_opacity * fade);
    
    color = cloudColor;
}