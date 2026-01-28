#version 330 core

in vec2 fragmentTexCoord;
out vec4 color;

uniform sampler2D imageTexture;
uniform float blurRadius;
uniform float weights[64];
uniform vec2 direction;

void main()
{
    int r = int(ceil(blurRadius));
    vec2 texel = 1.0 / textureSize(imageTexture, 0);

    vec4 accum = vec4(0.0);
    float totalWeight = 0.0;

    // Center tap
    for (int i = -r; i <= r; ++i) {
        vec2 offset = direction * float(i) * texel;
        vec2 uv = clamp(fragmentTexCoord + offset, vec2(0.0), vec2(1.0));
        vec4 sampleColor = texture(imageTexture, uv);

        float w = weights[i + r];
        // Input is already premultiplied in this pipeline.
        accum.rgb += sampleColor.rgb * w;
        accum.a   += sampleColor.a * w;
        totalWeight += w;
    }

    totalWeight = max(totalWeight, 1e-6);
    accum /= totalWeight;

    // Keep premultiplied output; pipeline uses premult blending.
    color = accum;
}
