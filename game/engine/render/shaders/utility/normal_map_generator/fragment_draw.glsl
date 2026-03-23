#version 330 core

in vec2 fragmentTexCoord;

uniform sampler2D imageTexture;
uniform vec2 texel_size;
uniform float smooth_strength;

out vec4 color;

void main()
{
    vec4 center_sample = texture(imageTexture, fragmentTexCoord);
    if (center_sample.a <= 0.0) {
        color = vec4(0.5, 0.5, 1.0, 0.0);
        return;
    }

    vec3 center_normal = center_sample.rgb * 2.0 - 1.0;
    vec3 accum = center_normal;
    float weight_sum = 1.0;

    for (int ox = -1; ox <= 1; ++ox) {
        for (int oy = -1; oy <= 1; ++oy) {
            if (ox == 0 && oy == 0) {
                continue;
            }

            vec2 offset = vec2(float(ox), float(oy)) * texel_size;
            vec4 sample_color = texture(imageTexture, fragmentTexCoord + offset);
            if (sample_color.a <= 0.0) {
                continue;
            }

            vec3 sample_normal = sample_color.rgb * 2.0 - 1.0;
            float weight = 1.0;
            if (ox == 0 || oy == 0) {
                weight = 2.0;
            }

            accum += sample_normal * weight * smooth_strength;
            weight_sum += weight * smooth_strength;
        }
    }

    vec3 smoothed = normalize(accum / weight_sum);
    color = vec4(smoothed * 0.5 + 0.5, center_sample.a);
}
