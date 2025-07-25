#version 330 core

in vec2 fragmentTexCoord;
out vec4 color;

// Animation uniforms
uniform float progress = 0.0; // 0.0 to 1.0
uniform float derive_progress = 0.0; // 0.0 = use progress, -1.0 = use time, 1.0 = use lifetime
uniform float ease_progress = 0.0; // 0.0 = no easing, -1.0 = ease in, 1.0 = ease out
uniform float time_scale = 1.0;
uniform float anim_rot_amt = 1.0;
uniform float time = 0.0; // Pass current time from your game
uniform float lifetime = 0.0; // For particle effects

// Shape uniforms
uniform sampler2D base_noise; // Main rough shape texture (should be stretched wide)
uniform sampler2D width_gradient_mask; // Clips width (white = clip, black = keep)
uniform sampler2D length_gradient_mask; // Clips length and controls animation
uniform sampler2D highlight; // Overlay texture
uniform float zoom = 0.6; // Scale (inverted - smaller = bigger)
uniform float rotate_all = 0.0; // Rotation in degrees

// Coloring uniforms  
uniform float emission_strength = 1.0;
uniform float mix_strength = 1.0;
uniform sampler2D color_lookup; // Color gradient lookup
uniform vec4 input_color = vec4(1.0); // Input color from sprite/quad

const float PI = 3.14159265359;

vec2 rotate(vec2 uv, vec2 pivot, float angle) {
    float s = sin(angle);
    float c = cos(angle);
    mat2 rotation = mat2(s, -c, c, s);
    uv -= pivot;
    uv = uv * rotation;
    uv += pivot;
    return uv;
}

// Convert to polar but focus on creating a slash pattern
vec2 slash_coordinates(vec2 uv, vec2 center, float zoom_factor) {
    vec2 dir = uv - center;
    float radius = length(dir);
    float angle = atan(dir.y, dir.x);
    
    // Normalize angle to 0-1 range
    float norm_angle = (angle + PI) / (2.0 * PI);
    
    // Create the slash mapping - this is key for the slash effect
    // We want to map the space so that the slash sweeps across
    float slash_u = radius * zoom_factor * 2.0;
    float slash_v = norm_angle;
    
    return vec2(slash_u, slash_v);
}

// Easing functions
float easeOutExpo(float x) {
    return x >= 1.0 ? 1.0 : 1.0 - pow(2.0, -10.0 * x);
}

float easeInExpo(float x) {
    return x <= 0.0 ? 0.0 : pow(2.0, 10.0 * x - 10.0);
}

float easeInOut(float x) {
    if (x < 0.5) {
        return (1.0 - sqrt(1.0 - pow(2.0 * x, 2.0))) / 2.0;
    } else {
        return (sqrt(1.0 - pow(-2.0 * x + 2.0, 2.0)) + 1.0) / 2.0;
    }
}

float get_progress() {
    float p;
    
    if (derive_progress > 0.0) {
        p = lifetime;
    } else if (derive_progress < 0.0) {
        p = mod(time * time_scale, 1.0);
    } else {
        p = progress;
    }
    
    if (ease_progress > 0.0) {
        return easeOutExpo(p);
    } else if (ease_progress < 0.0) {
        return easeInExpo(p);
    } else {
        return p;
    }
}

void main() {
    vec2 uv = fragmentTexCoord;
    float p = get_progress();
    
    // Apply global rotation first
    vec2 rotated_uv = rotate(uv, vec2(0.5), radians(rotate_all));
    
    // Convert to slash coordinates
    vec2 slash_uv = slash_coordinates(rotated_uv, vec2(0.5), zoom);
    
    // Sample base noise - animate by moving the pattern along the angle (v coordinate)
    vec4 base = texture(base_noise, slash_uv + vec2(0.0, -p));
    
    // Sample width mask - this should clip the width of the slash
    vec4 width_mask = texture(width_gradient_mask, slash_uv);
    
    // Sample length mask with rotation animation
    vec2 animated_slash_uv = slash_uv + vec2(0.0, -easeInOut(p * anim_rot_amt));
    vec2 rotated_length_uv = rotate(animated_slash_uv, vec2(0.5), radians(180.0));
    vec4 length_mask = texture(length_gradient_mask, rotated_length_uv);
    
    // Combine masks - subtract masks from base to create the slash shape
    vec4 shape = (base - width_mask) - length_mask;
    
    // Apply color lookup
    float lookup_coord = clamp(shape.r * uv.x, 0.0, 1.0);
    vec3 color_from_lookup = texture(color_lookup, vec2(lookup_coord, 0.0)).rgb * mix_strength;
    vec3 albedo = vec3(1.0) * color_from_lookup;
    
    // Add highlight
    vec4 highlight_sample = texture(highlight, slash_uv);
    vec4 highlight_masked = clamp(highlight_sample - length_mask, 0.0, 1.0);
    
    // Combine colors
    vec3 final_rgb = clamp(albedo + highlight_masked.rgb, 0.0, 1.0);
    final_rgb *= clamp(albedo + highlight_masked.rgb, 0.0, 1.0) * (3.0 * emission_strength);
    
    // Calculate animated alpha
    float alpha_phase = abs(cos(p * PI));
    float shape_alpha = smoothstep(alpha_phase, alpha_phase, shape.r);
    float highlight_alpha = smoothstep(
        clamp(alpha_phase, 0.0, 0.2), 
        clamp(alpha_phase, 0.0, 0.2), 
        highlight_masked.r * 0.2
    );
    
    float final_alpha = clamp(shape_alpha + highlight_alpha, 0.0, 1.0) * input_color.a;
    
    color = vec4(final_rgb, final_alpha);
}