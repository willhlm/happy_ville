#version 330 core

in vec2 fragmentTexCoord; // [0,1] UV coordinates
uniform sampler2D SCREEN_TEXTURE;

out vec4 COLOR;

uniform float TIME;
uniform float spin_rotation_speed = 2.0;
uniform float move_speed = 7.0;
uniform vec2 offset = vec2(0., 0.);
uniform float spin_amount = 0.25;
uniform float pixel_filter = 740.;
uniform bool is_rotating = false;

uniform vec2 camera_world_pos;
uniform float zoom = 1.0;

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

    pos *= 30.0;
    float time_speed = TIME * move_speed;
    vec2 uv2 = vec2(pos.x + pos.y);

    for (int i = 0; i < 5; i++) {
        uv2 += sin(max(pos.x, pos.y)) + pos;
        pos += 0.5 * vec2(
            cos(5.1123314 + 0.353 * uv2.y + time_speed * 0.131121),
            sin(uv2.x - 0.113 * time_speed)
        );
        pos -= cos(pos.x + pos.y) - sin(pos.x * 0.711 - pos.y);
    }

    // Add back to original UVs (not screen_coords!)
    vec2 final_uv = uv + pos * 0.001;

    // Clamp to valid texture range
    return clamp(final_uv, 0.0, 1.0);
}

void main() {
    vec2 screenSize = vec2(640.0, 360.0); // Ideally pass this as a uniform
    vec2 world_pos = camera_world_pos + (fragmentTexCoord - 0.5) * screenSize / zoom;

    vec2 distorted_uv = distort_uv(fragmentTexCoord, screenSize);
    COLOR = texture(SCREEN_TEXTURE, distorted_uv);
}
