#version 330 core

in vec2 fragmentTexCoord; // [0,1] UV coordinates
uniform sampler2D SCREEN_TEXTURE;
uniform sampler2D NOISE_TEXTURE;

out vec4 COLOR;

uniform float TIME;
uniform float spin_rotation_speed = 2.0;
uniform float move_speed = 7.0;
uniform vec2 offset = vec2(0., 0.);
uniform float spin_amount = 1;
uniform float pixel_filter = 740.;
uniform bool is_rotating = false;
uniform float distortion_strength = 0.001;
uniform float noise_scale = 1.0;

#define SPIN_EASE 1.0

vec2 distort_uv(vec2 uv, vec2 screenSize) {
    float pixel_size = length(screenSize) / pixel_filter;

    // Convert to pseudo-screen space for distortion
    vec2 pos = (floor(uv * screenSize / pixel_size) * pixel_size - 0.5 * screenSize) / length(screenSize) - offset;
    float pos_len = length(pos);

    float speed = spin_rotation_speed * SPIN_EASE * 0.2;
    if (is_rotating) {
        speed = TIME * speed;
    }
    speed += 302.2;

    float angle = atan(pos.y, pos.x) + speed - SPIN_EASE * 20.0 * (spin_amount * pos_len + (1.0 - spin_amount));
    vec2 mid = (screenSize / length(screenSize)) / 2.0;
    pos = vec2(pos_len * cos(angle) + mid.x, pos_len * sin(angle) + mid.y) - mid;

    // Replace the procedural noise with texture sampling
    vec2 noise_uv = (uv + offset) * noise_scale;
    vec2 time_offset = vec2(TIME * move_speed * 0.01, TIME * move_speed * 0.013);
    noise_uv += time_offset;
    
    // Sample the noise texture
    vec2 noise = texture(NOISE_TEXTURE, fract(noise_uv)).xy;
    // Convert noise from [0,1] to [-1,1] range
    noise = (noise - 0.5) * 2.0;
    
    // Combine the spinning distortion with the noise
    vec2 combined_distortion = pos * 30.0 + noise * 100.0;

    // Add back to original UVs
    vec2 final_uv = uv + combined_distortion * distortion_strength;

    // Clamp to valid texture range
    return clamp(final_uv, 0.0, 1.0);
}

void main() {
    vec2 screenSize = vec2(640.0, 360.0); // Ideally pass this as a uniform

    vec2 distorted_uv = distort_uv(fragmentTexCoord, screenSize);
    COLOR = texture(SCREEN_TEXTURE, distorted_uv);
}