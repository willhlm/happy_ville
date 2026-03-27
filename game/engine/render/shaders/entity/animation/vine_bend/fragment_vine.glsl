#version 330 core

in vec2 fragmentTexCoord;
out vec4 color;

uniform sampler2D imageTexture;
uniform float TIME;
uniform float offset;
uniform int point_count;
uniform float point_offsets[12];
uniform float body_left = 0.0;
uniform float body_right = 1.0;
uniform float wind_strength = 0.012;
uniform float edge_flutter = 0.008;

float sample_chain_offset(float y)
{
    if (point_count <= 1) {
        return 0.0;
    }

    float scaled = clamp(y, 0.0, 1.0) * float(point_count - 1);
    int index_a = int(floor(scaled));
    int index_b = min(index_a + 1, point_count - 1);
    float mix_value = fract(scaled);

    return mix(point_offsets[index_a], point_offsets[index_b], mix_value);
}

void main()
{
    float body_width = max(0.0001, body_right - body_left);
    if (fragmentTexCoord.x < body_left || fragmentTexCoord.x > body_right) {
        color = texture(imageTexture, fragmentTexCoord);
        return;
    }

    float local_x = (fragmentTexCoord.x - body_left) / body_width;
    float chain_y = 1.0 - fragmentTexCoord.y;
    float chain_offset = sample_chain_offset(chain_y);
    float root_falloff = smoothstep(0.04, 0.25, chain_y);
    float side_mask = sin(local_x * 3.14159265);
    float flutter = sin(TIME * 0.055 + offset + chain_y * 8.0) * wind_strength * root_falloff;
    flutter += sin(TIME * 0.09 + offset * 1.7 + chain_y * 18.0) * edge_flutter * root_falloff * side_mask;

    float shifted_local_x = local_x + (chain_offset + flutter) / body_width;
    if (shifted_local_x < 0.0 || shifted_local_x > 1.0) {
        color = vec4(0.0);
        return;
    }

    vec2 modifiedTexCoord = vec2(body_left + shifted_local_x * body_width, fragmentTexCoord.y);
    color = texture(imageTexture, modifiedTexCoord);
}
