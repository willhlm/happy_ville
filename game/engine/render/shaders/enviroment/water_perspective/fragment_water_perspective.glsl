#version 330 core

in vec2 fragmentTexCoord;
out vec4 colour;
uniform sampler2D imageTexture;

uniform vec4 water_albedo = vec4(0.26, 0.23, 0.73, 1.0);
uniform float water_opacity = 0.35;
uniform float water_speed = 0.1;
uniform float wave_distortion = 0.07;
uniform float water_texture_limit = 0.45;
uniform int wave_multiplier = 6;
uniform bool water_texture_on = true;
uniform float reflection_X_offset = 0.0;
uniform float reflection_Y_offset = 0.0;
uniform sampler2D noise_texture;
uniform sampler2D noise_texture2;
uniform float TIME;
uniform vec2 u_resolution = vec2(640, 360);
uniform sampler2D SCREEN_TEXTURE;
uniform vec4 section;   // Full scroll (for water texture positioning)
uniform vec4 section0;  // No Y scroll (for rendering position)

uniform float texture_parallax = 1;

void main() {
    // fragmentTexCoord is based on section0 (no Y scroll)
    vec2 normalizedSectionPos0 = vec2(section0.x / u_resolution.x, section0.y / u_resolution.y);
    vec2 normalizedSectionSize0 = vec2(section0.z / u_resolution.x, section0.w / u_resolution.y);        
    vec2 normalizedTexCoord0 = (fragmentTexCoord - normalizedSectionPos0) / normalizedSectionSize0;

    // Calculate coordinate in section space (with full scroll) for water texture
    vec2 normalizedSectionPos = vec2(section.x / u_resolution.x, section.y / u_resolution.y);
    vec2 normalizedSectionSize = vec2(section.z / u_resolution.x, section.w / u_resolution.y);
    vec2 fragmentTexCoordInSectionSpace = normalizedSectionPos + normalizedTexCoord0 * normalizedSectionSize;

    vec4 COLOR = vec4(0.0);
    COLOR.a = 1.0;

    // Water waves
    vec2 water_uv = vec2(fragmentTexCoord.x, fragmentTexCoord.y * float(wave_multiplier));
    float noise = texture(noise_texture, vec2(water_uv.x + TIME * water_speed, water_uv.y)).x * wave_distortion;

    if (water_texture_on) {
        // Water texture uses section space coordinates
        vec2 water_texture_coord = (vec2(fragmentTexCoordInSectionSpace.x * pow(normalizedTexCoord0.y, texture_parallax), fragmentTexCoordInSectionSpace.y) + vec2(TIME * water_speed, 0.0));
        vec4 water_texture = texture(noise_texture2, water_texture_coord);
        float water_texture_value = (water_texture.x < water_texture_limit) ? 0.0 : 1.0;
        COLOR.xyz = vec3(1.0) * water_texture_value;
    }

    // For reflection: we want to sample from where the content is in SCREEN_TEXTURE
    // SCREEN_TEXTURE was rendered with full camera scroll (section)
    // So we need to use section coordinates for sampling
    vec4 current_texture = texture(SCREEN_TEXTURE, vec2(fragmentTexCoordInSectionSpace.x + noise + reflection_X_offset, -fragmentTexCoordInSectionSpace.y + reflection_Y_offset));

    COLOR = mix(COLOR, current_texture, 0.5);
    COLOR = mix(COLOR, water_albedo, water_opacity);

    float transitionRange = 0.1;
    COLOR.a *= smoothstep(0.0, transitionRange, abs(1-normalizedTexCoord0.y));

    colour = COLOR;
}