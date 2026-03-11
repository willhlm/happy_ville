#version 330 core

in vec2 fragmentTexCoord;
out vec4 color;

uniform sampler2D imageTexture;
uniform int r;                 // integer radius (<= 31 recommended)
uniform float weights[64];     // weights[0..r] used (1D gaussian, normalized)

void main()
{
    vec2 texel = 1.0 / vec2(textureSize(imageTexture, 0));

    vec4 accum = vec4(0.0);
    float total = 0.0;

    for (int y = -r; y <= r; ++y) {
        float wy = weights[abs(y)];
        for (int x = -r; x <= r; ++x) {
            float wx = weights[abs(x)];
            float w = wx * wy;

            vec4 s = texture(imageTexture, fragmentTexCoord + vec2(x, y) * texel);

            // assumes PREMULTIPLIED input (recommended)
            accum += s * w;
            total += w;
        }
    }

    color = accum / max(total, 1e-6);
}
