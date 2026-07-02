#version 330 core

in vec2 fragmentTexCoord; // top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture; // texture in location 0
uniform sampler2D SCREEN_TEXTURE;

// Nebula effect uniforms
uniform float time = 0.0;
uniform vec2 resolution = vec2(800.0, 600.0);
uniform vec4 albedo = vec4(1.0, 0.5, 0.3, 1.0);
uniform vec2 center = vec2(0.5, 0.5); // Center of the nebula effect
uniform vec4 section = vec4(0.0, 0.0, 800.0, 600.0);

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

float NebulaNoise(vec3 p, float anim) {
    p.xy += vec2(
        sin(anim * 0.9 + p.z * 0.7),
        cos(anim * 0.7 + p.x * 0.5)
    ) * 0.18;
    p.z += sin(anim * 0.5 + p.y * 0.6) * 0.35;

    float final = p.y + 4.5;
    final -= SpiralNoiseC(p.xyz);   // mid-range noise
    final += SpiralNoiseC(p.zxy * 0.5123 + 100.0 + vec3(anim * 0.06))*4.0;   // large scale features
    return final;
}

float myMap(vec3 p, float anim) {
    float NebNoise = abs(NebulaNoise(p / 0.5, anim) * 0.5) + 0.03;
    return NebNoise;
}

void main() {
    // Convert fragment coordinates to normalized device coordinates
    vec2 uv = fragmentTexCoord;
    
    // Convert to centered coordinates (-1 to 1)
    vec2 coord = (uv - 0.5) * 2.0;
    
    // Adjust for aspect ratio
    coord.x *= resolution.x / resolution.y;

    vec2 screenSize = vec2(textureSize(SCREEN_TEXTURE, 0));
    vec2 normalizedSectionPos = vec2(section.x, section.y) / screenSize;
    vec2 normalizedSectionSize = vec2(section.z, section.w) / screenSize;
    vec2 screenUV = uv * normalizedSectionSize + vec2(
        normalizedSectionPos.x,
        1.0 - normalizedSectionPos.y - normalizedSectionSize.y
    );
    
    float baseTime = 10.0;
    float anim = time;

    // Keep the effect anchored near the slice that looks good around time = 10
    vec3 world_pos = vec3(coord.x * 5.0, coord.y * 5.0, baseTime * 0.1);
    world_pos.xy += vec2(
        sin(anim * 0.35),
        cos(anim * 0.28 + 1.3)
    ) * 0.08;
    
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
        
        d = myMap(pos, anim);
        d = max(d, 0.08);
        
        // STAR in CENTER - calculate distance from center
        vec2 center_offset = (center - 0.5) * 2.0;
        center_offset.x *= resolution.x / resolution.y;
        vec3 star_center = vec3(center_offset, 0.0);
        vec3 ldst = star_center - pos;
        float lDist = max(length(ldst), 0.001);
        
        // Add center glow with a mild pulse instead of a full shape drift
        sum.rgb += (albedo.rgb / (lDist * lDist) / 30.0);
        sum.rgb *= 0.992 + 0.008 * sin(anim * 0.8);
        
        td += 1.0 / 50.0; // Adjusted for 2D
        d = max(d, 0.04);
        t += max(d * 0.1 * max(min(length(ldst), length(world_pos)), 1.0), 0.02);
    }
    
    float distToCenter = length(coord);
    float radialMask = smoothstep(1.05, 0.18, distToCenter);
    vec2 dir = distToCenter > 0.0001 ? coord / distToCenter : vec2(0.0, 0.0);
    vec2 tangent = vec2(-dir.y, dir.x);
    vec3 rawNebula = sum.rgb * t;
    float rawNebulaAlpha = clamp(max(max(rawNebula.r, rawNebula.g), rawNebula.b), 0.0, 1.0);

    float lensFalloff = radialMask * (1.0 - smoothstep(0.0, 0.16, distToCenter));
    float innerCompression = smoothstep(0.32, 0.06, distToCenter) * radialMask;
    float ringShear = smoothstep(0.18, 0.34, distToCenter) * (1.0 - smoothstep(0.34, 0.62, distToCenter));
    float corePulse = 0.94 + 0.06 * sin(anim * 0.35);
    float angularDrift = sin(anim * 0.28 + atan(coord.y, coord.x) * 4.0);

    vec2 distortion = vec2(0.0);
    distortion -= dir * (0.032 * lensFalloff * corePulse);
    distortion -= dir * (0.02 * innerCompression);
    distortion += tangent * (0.02 * ringShear * angularDrift);
    distortion += coord * (rawNebulaAlpha * 0.003 * radialMask);

    vec4 refractedColor = texture(SCREEN_TEXTURE, clamp(screenUV + distortion, 0.0, 1.0));

    float coreMask = smoothstep(0.32, 0.03, distToCenter);
    float compressedHalo = smoothstep(0.48, 0.16, distToCenter) * (1.0 - coreMask);
    float veilMask = smoothstep(0.82, 0.38, distToCenter) * (1.0 - smoothstep(0.18, 0.42, distToCenter));

    vec3 coreColor = albedo.rgb * (1.1 + 0.35 * rawNebulaAlpha) * coreMask;
    vec3 haloColor = mix(albedo.rgb, vec3(0.45, 0.55, 0.68), 0.65) * compressedHalo * (0.35 + 0.2 * rawNebulaAlpha);
    vec3 veilColor = vec3(0.04, 0.05, 0.08) * veilMask;
    vec3 nebulaColor = coreColor + haloColor + veilColor;
    float nebulaAlpha = clamp(coreMask * 0.72 + compressedHalo * 0.24 + veilMask * 0.08 + rawNebulaAlpha * 0.18, 0.0, 1.0);

    vec3 voidTint = mix(refractedColor.rgb, refractedColor.rgb * 0.12, radialMask * (0.45 + 0.4 * nebulaAlpha));
    vec3 glowColor = voidTint + nebulaColor;
    float effectMask = clamp(radialMask * 0.68 + nebulaAlpha * 0.85, 0.0, 1.0);
    vec3 finalColor = mix(refractedColor.rgb, glowColor, clamp(nebulaAlpha * 0.72 + radialMask * 0.14, 0.0, 1.0));

    color = vec4(finalColor, effectMask);
}
