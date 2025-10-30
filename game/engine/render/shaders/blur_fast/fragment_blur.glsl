#version 330 core

in vec2 fragmentTexCoord;
out vec4 color;

uniform sampler2D imageTexture;
uniform float blurRadius;
uniform float weights[64];
uniform vec2 direction;

void main()
{
    int r = int(blurRadius);
    vec2 texel = 1.0 / textureSize(imageTexture, 0);

    vec4 accum = vec4(0.0);
    float totalWeight = 0.0;

    for (int i = -r; i <= r; ++i) {
        vec2 offset = direction * float(i) * texel;
        vec4 sampleColor = texture(imageTexture, fragmentTexCoord + offset);

        float w = weights[i + r];
        accum += sampleColor * w;
        totalWeight += w;
    }

    accum /= totalWeight;

    // straight (non-premultiplied) RGBA out
    color = accum;
}
