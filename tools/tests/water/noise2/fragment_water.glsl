#version 330 core

in vec2 fragmentTexCoord;
out vec4 colour;

uniform float level= 0.5;
uniform vec4 water_albedo  = vec4(0.26, 0.23, 0.73, 1.0);
uniform float water_opacity  = 0.35;
uniform float water_speed = 0.2;
uniform float wave_distortion = 0.1;
float water_texture_limit = 0.45;
uniform int wave_multiplyer = 7;
uniform bool water_texture_on = true;
uniform float reflection_X_offset = 0.0;
uniform float reflection_Y_offset = 0.0;
uniform sampler2D noise_texture;
uniform sampler2D noise_texture2;
uniform float TIME;

uniform sampler2D SCREEN_TEXTURE ;

void main() {
    vec2 uv = fragmentTexCoord;
    vec4 COLOR = vec4(0.0);

    if (uv.y <= level) {
        COLOR.a = 1.0;

        // distorted reflections
        vec2 water_uv = vec2(uv.x, uv.y * float(wave_multiplyer));
        float noise = texture(noise_texture, vec2(water_uv.x + TIME * water_speed, water_uv.y)).x * wave_distortion;
        noise -= (0.5 * wave_distortion);

        // water texture
        if (water_texture_on) {
            vec4 water_texture = texture(noise_texture2, uv * vec2(0.5, 4.0) + vec2(noise, 0.0));
            float water_texture_value = (water_texture.x > water_texture_limit) ? 0.0 : 1.0;
            COLOR.xyz = vec3(1.0) * water_texture_value;
        }

        // reflect screen texture
        vec4 current_texture = texture(SCREEN_TEXTURE, vec2(fragmentTexCoord.x + noise + reflection_X_offset, 1.0 - fragmentTexCoord.y - (level - 0.5) * 2.0 + reflection_Y_offset));

        //COLOR = mix(COLOR, current_texture, 0.5);
        //COLOR = mix(COLOR, water_albedo, water_opacity);

        COLOR.xyz = mix(COLOR.rgb, water_albedo.rgb, min(COLOR.r,0.5));
        COLOR.xyz = mix(COLOR.rgb, current_texture.rgb, min(COLOR.r,water_opacity));

        COLOR.xyz = mix(COLOR.rgb, vec3(1.0), step(COLOR.rgb, vec3(0.00001)));
    }
    colour = COLOR;
}
