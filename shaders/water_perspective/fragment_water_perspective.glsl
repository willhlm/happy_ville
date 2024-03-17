#version 330 core

in vec2 fragmentTexCoord;
out vec4 colour;
uniform sampler2D imageTexture;// texture in location 0

uniform vec4 water_albedo = vec4(0.26, 0.23, 0.73, 1.0);
uniform float water_opacity = 0.35;
uniform float water_speed = 0.1;//0.1
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
uniform vec2 scroll;
uniform sampler2D SCREEN_TEXTURE;
uniform vec4 section;
uniform float texture_parallax = 1;//flag for if the texture should have parallax

void main() {
    vec2 normalizedSectionPos = vec2(section.x / u_resolution.x, section.y / u_resolution.y);
    vec2 normalizedSectionSize = vec2(section.z / u_resolution.x, section.w / u_resolution.y);
    vec2 normalizedTexCoord2 = (fragmentTexCoord - normalizedSectionPos) / normalizedSectionSize;

    vec4 COLOR = vec4(0.0);
    COLOR.a = 1.0;

    vec2 water_uv = vec2(fragmentTexCoord.x, fragmentTexCoord.y * float(wave_multiplier));
    float noise = texture(noise_texture, vec2(water_uv.x + TIME * water_speed, water_uv.y)).x * wave_distortion;

    if (water_texture_on) {
        vec2 water_texture_coord = (vec2(fragmentTexCoord.x * pow(normalizedTexCoord2.y,texture_parallax), fragmentTexCoord.y) + vec2(TIME * water_speed, 0.0));
        vec4 water_texture = texture(noise_texture2, water_texture_coord);
        float water_texture_value = (water_texture.x < water_texture_limit) ? 0.0 : 1.0;
        COLOR.xyz = vec3(1.0) * water_texture_value;
    }

    vec4 current_texture = texture(SCREEN_TEXTURE, vec2(fragmentTexCoord.x + noise + reflection_X_offset, -fragmentTexCoord.y + reflection_Y_offset));

    COLOR = mix(COLOR, current_texture, 0.5);
    COLOR = mix(COLOR, water_albedo, water_opacity);

    colour = COLOR;
}
