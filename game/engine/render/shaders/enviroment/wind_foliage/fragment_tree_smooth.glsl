#version 330 core

in vec2 fragmentTexCoord;
in vec2 worldPosition;

uniform sampler2D imageTexture;
uniform float time;

// Wind parameters
uniform float wind_strength = 1.0;
uniform float wind_speed = 0.5;
uniform vec2 wind_direction = vec2(1.0, 0.0);

// Depth-based animation
uniform float depth_layers = 5.0;           // Number of depth layers
uniform float depth_separation = 0.04;      // How much layers separate
uniform float depth_wave_scale = 1.5;       // Wave intensity scales with depth
uniform float shimmer_amount = 0.007;        // Fast flutter on near layers

// Voronoi clustering (for variation within layers)
uniform float leaf_cell_size = 0.002;

// Branch sway
uniform float branch_sway = 0.03;
uniform float cross_wind_amount = 0.2;      // How much perpendicular movement (0-1)

// Anchor point
uniform vec2 anchor_point = vec2(0.5, 0.2);

out vec4 color;

// Hash functions
float hash12(vec2 p) {
    float h = dot(p, vec2(127.1, 311.7));
    return fract(sin(h) * 43758.5453123);
}

vec2 hash22(vec2 p) {
    p = vec2(dot(p, vec2(127.1, 311.7)),
             dot(p, vec2(269.5, 183.3)));
    return fract(sin(p) * 43758.5453123);
}

// Voronoi for local variation
vec2 voronoiID(vec2 p) {
    vec2 i = floor(p);
    vec2 f = fract(p);
    
    float min_dist = 10.0;
    vec2 cell_id = vec2(0.0);
    
    for (int y = -1; y <= 1; y++) {
        for (int x = -1; x <= 1; x++) {
            vec2 neighbor = vec2(float(x), float(y));
            vec2 cell = i + neighbor;
            vec2 rand_point = hash22(cell);
            vec2 point_pos = neighbor + rand_point;
            
            float dist = length(point_pos - f);
            
            if (dist < min_dist) {
                min_dist = dist;
                cell_id = cell;
            }
        }
    }
    
    return cell_id;
}

// Extract depth from texture
// Brighter pixels = closer (foreground leaves)
// Darker pixels = further (background, branches)
float getDepth(vec2 uv) {
    vec4 texel = texture(imageTexture, uv);
    
    // Use luminance as depth proxy
    float luminance = dot(texel.rgb, vec3(0.299, 0.587, 0.114));
    
    // Optional: boost contrast for clearer layers
    luminance = pow(luminance, 0.8);  // Adjust this: <1 = more contrast
    
    return luminance;
}

// Quantize depth into discrete layers
float quantizeDepth(float depth, float num_layers) {
    return floor(depth * num_layers) / num_layers;
}

void main()
{
    vec2 uv = fragmentTexCoord;
    
    // Normalize wind direction
    vec2 dir = normalize(wind_direction);
    vec2 perp = vec2(-dir.y, dir.x);
    
    // Distance from anchor
    vec2 to_anchor = uv - anchor_point;
    to_anchor.x *= 0.6;
    float distance_from_anchor = length(to_anchor);
    float movement_strength = distance_from_anchor * distance_from_anchor;
    
    // ============================================
    // GLOBAL BRANCH SWAY
    // ============================================
    float branch_time = time * wind_speed * 0.3;
    float branch_offset = sin(branch_time) * branch_sway;
    branch_offset += sin(branch_time * 1.4 + 2.1) * branch_sway * 0.4;
    vec2 global_sway = dir * branch_offset * movement_strength * wind_strength;
    
    // ============================================
    // SAMPLE INITIAL DEPTH
    // ============================================
    // Get depth from current position
    vec2 base_uv = uv + global_sway;
    float raw_depth = getDepth(base_uv);
    
    // Optional: quantize into discrete layers for more obvious effect
    // Comment out this line for smooth depth gradient
    float depth = quantizeDepth(raw_depth, depth_layers);
    // Uncomment for smooth: float depth = raw_depth;
    
    // ============================================
    // VORONOI CELL (for variation within same depth)
    // ============================================
    vec2 cell_id = voronoiID(worldPosition * leaf_cell_size);
    float cell_seed1 = hash12(cell_id);
    float cell_seed2 = hash12(cell_id + vec2(17.3, 53.7));
    
    // Each cell has unique timing
    float cell_phase = cell_seed1 * 6.2831853;
    float cell_freq = 0.8 + cell_seed2 * 0.5;
    float cell_time = time * wind_speed * cell_freq + cell_phase;
    
    // ============================================
    // DEPTH-BASED PARALLAX DISPLACEMENT
    // ============================================
    // Key concept: Closer layers (higher depth) move MORE
    // Further layers (lower depth) move LESS
    
    // Parallax multiplier based on depth
    // depth = 0.0 (dark/far) → multiplier = 0.0 (no movement)
    // depth = 1.0 (bright/near) → multiplier = 1.0 (full movement)
    float parallax_factor = depth;
    
    // Apply depth-scaled movement
    vec2 depth_offset = global_sway * parallax_factor * depth_separation;
    
    // ============================================
    // WAVE MOTION (scaled by depth)
    // ============================================
    // Foreground leaves wave more than background
    
    // Primary wave (along wind direction)
    float primary_wave = sin(cell_time * 2.0) * (1.0 + sin(cell_time * 0.6) * 0.3);
    
    // Secondary wave (perpendicular to wind - much smaller)
    float secondary_wave = sin(cell_time * 2.4 + cell_seed2 * 3.14) * 0.5;
    
    // Combine: mostly in wind direction, some perpendicular
    vec2 wave = dir * primary_wave + perp * secondary_wave * cross_wind_amount;
    
    // Scale by base amount, movement strength, wind strength, and depth
    wave *= 0.03  // Base wave amount
          * movement_strength 
          * wind_strength
          * (0.3 + parallax_factor * depth_wave_scale);  // Scale by depth!
    
    // ============================================
    // SHIMMER (high-frequency flutter)
    // ============================================
    // Only foreground leaves shimmer
    float shimmer_intensity = smoothstep(0.4, 0.8, depth);  // Only bright areas
    
    // Shimmer mostly in wind direction
    float shimmer_primary = sin(cell_time * 5.0);
    float shimmer_cross = sin(cell_time * 6.2 + cell_seed1 * 6.28);
    
    vec2 shimmer = (dir * shimmer_primary + perp * shimmer_cross * cross_wind_amount * 0.5)
                 * shimmer_amount 
                 * shimmer_intensity 
                 * movement_strength 
                 * wind_strength;
    
    // ============================================
    // COMBINE ALL DISPLACEMENTS
    // ============================================
    vec2 total_offset = depth_offset  // Parallax (depth-based)
                      + wave          // Wave motion (depth-scaled)
                      + shimmer;      // Flutter (foreground only)
    
    // ============================================
    // ITERATIVE DEPTH SAMPLING (Parallax Occlusion)
    // ============================================
    // This creates proper layering by resampling depth
    
    vec2 final_uv = base_uv + total_offset;
    
    // Optionally resample depth at new position for better parallax
    // This makes layers "slide over" each other more convincingly
    float resampled_depth = getDepth(final_uv);
    
    // If we moved to a different depth layer, adjust slightly
    float depth_difference = resampled_depth - depth;
    vec2 depth_correction = total_offset * depth_difference * 0.3;
    
    final_uv -= depth_correction;
    
    // Clamp to texture bounds
    final_uv = clamp(final_uv, 0.0, 1.0);
    
    // ============================================
    // FINAL SAMPLE
    // ============================================
    color = texture(imageTexture, final_uv);
    
    // ============================================
    // DEPTH-BASED BRIGHTNESS (depth cue)
    // ============================================
    // Foreground slightly brighter (more light)
    float brightness = 1.0 + depth * 0.08;
    
    // Moving leaves catch more light
    float motion = length(wave + shimmer);
    brightness += motion * 0.12;
    
    color.rgb *= brightness;
    
    // ============================================
    // DEBUG: Visualize depth layers (optional)
    // ============================================
    // Uncomment to see depth layers as colored overlays
    // float layer = quantizeDepth(raw_depth, depth_layers);
    // color.rgb = mix(color.rgb, vec3(layer), 0.3);
}
