#version 330 core

in vec2 fragmentTexCoord;
out vec4 colour;
uniform sampler2D imageTexture;// texture in location 0

uniform vec4 water_albedo = vec4(0.26, 0.23, 0.73, 1.0);
uniform float water_opacity = 0.35;
uniform float water_speed = 0.1;
uniform float wave_distortion = 0.07;
float water_texture_limit = 0.45;
uniform int wave_multiplyer = 6;
uniform bool water_texture_on = true;
uniform float reflection_X_offset = 0.0;
uniform float reflection_Y_offset = 0.43;
uniform sampler2D noise_texture;
uniform sampler2D noise_texture2;
uniform float TIME;
uniform vec2 u_resolution = vec2(640, 360);
uniform vec2 scroll;

uniform sampler2D SCREEN_TEXTURE;

void main() {
    // Calculate normalized texture coordinates
    vec2 normalizedTexCoord = fragmentTexCoord;

    vec4 COLOR = vec4(0.0);
    COLOR.a = 1.0;

    // Distorted reflections
    vec2 water_uv = vec2(normalizedTexCoord.x, normalizedTexCoord.y * float(wave_multiplyer));
    float noise = texture(noise_texture, vec2(water_uv.x + TIME * water_speed, water_uv.y)).x * wave_distortion;
    //noise -= (0.5 * wave_distortion);

    // Water texture
    if (water_texture_on) {// Apply the offset to the texture coordinates
        vec4 water_texture = texture(noise_texture2, (fragmentTexCoord) + vec2(TIME * water_speed,0));
        float water_texture_value = (water_texture.x < water_texture_limit) ? 0.0 : 1.0;

        COLOR.xyz = vec3(1.0) * water_texture_value;
    }

    vec2 textureSize_var = vec2(textureSize(imageTexture, 0).xy);
    float scale = textureSize_var.y/textureSize_var.x;
    // Reflect screen texture
    vec2 offset2 =  scroll - u_resolution*floor(scroll/u_resolution);

    vec4 current_texture = texture(SCREEN_TEXTURE, vec2((textureSize_var.x/u_resolution.x)*normalizedTexCoord.x + noise + offset2.x + reflection_X_offset, -normalizedTexCoord.y*(textureSize_var.y/u_resolution.y) + reflection_Y_offset));

    // Mix the water and screen texture
    COLOR = mix(COLOR, current_texture, 0.5);

    // Apply water albedo and opacity
    COLOR = mix(COLOR, water_albedo, water_opacity);

    colour = COLOR;
}
