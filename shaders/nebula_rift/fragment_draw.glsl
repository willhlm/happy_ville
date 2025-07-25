#version 330 core

in vec2 fragmentTexCoord; // top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture; // texture in location 0

// Nebula effect uniforms
uniform float time = 0.0;
uniform vec2 resolution = vec2(800.0, 600.0);
uniform vec4 albedo = vec4(1.0, 0.5, 0.3, 1.0);
uniform vec2 center = vec2(0.5, 0.5); // Center of the nebula effect

out vec4 color;

const float nudge = 0.739513;   // size of perpendicular vector
const float normalizer = 1.0 / sqrt(1.0 + nudge*nudge);   // pythagorean theorem on that perpendicular to maintain scale

float SpiralNoiseC(vec3 p) {
    float n = 0.0;
    float iter = 1.0;
    
    for (int i = 0; i < 8; i++) { 
        // add sin and cos scaled inverse with the frequency
        n += -abs(sin(p.y*iter) + cos(p.x*iter)) / iter;    // abs for a ridged look
        p.xy += vec2(p.y, -p.x) * nudge; // rotate by adding perpendicular and scaling down
        p.xy *= normalizer;
        p.xz += vec2(p.z, -p.x) * nudge; // rotate on other axis
        p.xz *= normalizer;
        iter *= 1.733733; // increase the frequency
    }
    
    return n;
}

float NebulaNoise(vec3 p) {
    float final = p.y + 4.5;
    final -= SpiralNoiseC(p.xyz);   // mid-range noise
    final += SpiralNoiseC(p.zxy*0.5123+100.0)*4.0;   // large scale features
    return final;
}

float myMap(vec3 p) {
    float NebNoise = abs(NebulaNoise(p/0.5) * 0.5) + 0.03;
    return NebNoise;
}

void main() {
    // Convert fragment coordinates to normalized device coordinates
    vec2 uv = fragmentTexCoord;
    
    // Convert to centered coordinates (-1 to 1)
    vec2 coord = (uv - 0.5) * 2.0;
    
    // Adjust for aspect ratio
    coord.x *= resolution.x / resolution.y;
    
    // Create a 3D position from 2D coordinates
    vec3 world_pos = vec3(coord.x * 5.0, coord.y * 5.0, time * 0.1);
    
    // Ray direction for 2D (we'll simulate depth by using a forward direction)
    vec3 ray_dir = normalize(vec3(coord.x * 0.1, coord.y * 0.1, 1.0));
    
    vec4 sum = vec4(0.0);
    float d = 1.0, t = 0.0;
    float td = 0.0;
    float min_dist = 0.0, max_dist = 10.0;
    
    t = min_dist * step(t, min_dist);
    
    // Raymarching loop (reduced iterations for 2D)
    for (int i = 0; i < 20; i++) {
        vec3 pos = world_pos + t * ray_dir;
        
        // break conditions
        if(td > 0.9 || d < 0.1*t || t > 5.0 || sum.a > 0.99 || t > max_dist) break;
        
        float d = myMap(pos);
        d = max(d, 0.08);
        
        // STAR in CENTER - calculate distance from center
        vec2 center_offset = (center - 0.5) * 2.0;
        center_offset.x *= resolution.x / resolution.y;
        vec3 star_center = vec3(center_offset, 0.0);
        vec3 ldst = star_center - pos;
        float lDist = max(length(ldst), 0.001);
        
        // Add star bloom effect
        sum.rgb += (albedo.rgb / (lDist * lDist) / 30.0);
        
        td += 1.0 / 50.0; // Adjusted for 2D
        d = max(d, 0.04);
        t += max(d * 0.1 * max(min(length(ldst), length(world_pos)), 1.0), 0.02);
    }
    
    // Combine with original texture
    vec4 originalColor = texture(imageTexture, fragmentTexCoord);
    
    vec3 nebulaColor = sum.rgb * t;
    float nebulaAlpha = clamp(nebulaColor.r + nebulaColor.g + nebulaColor.b, 0.0, 1.0);
    
    // Blend nebula effect with original texture
    color = mix(originalColor, vec4(nebulaColor, nebulaAlpha), nebulaAlpha * 0.8);
}