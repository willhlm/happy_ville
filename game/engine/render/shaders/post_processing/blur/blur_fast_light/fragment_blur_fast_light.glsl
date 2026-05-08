#version 330 core

in vec2 fragmentTexCoord;
out vec4 color;

uniform sampler2D imageTexture;
uniform int r;
uniform float weights[64];

void main()
{
    vec2 texel = 1.0 / vec2(textureSize(imageTexture, 0));

    vec3 accumRgb = vec3(0.0);
    float alphaAccum = 0.0;

    for (int y = -r; y <= r; ++y) {
        float wy = weights[abs(y)];
        for (int x = -r; x <= r; ++x) {
            float wx = weights[abs(x)];
            float w = wx * wy;

            vec4 s = texture(imageTexture, fragmentTexCoord + vec2(x, y) * texel);
            accumRgb += s.rgb * w * s.a;
            alphaAccum += w * s.a;
        }
    }

    accumRgb /= max(alphaAccum, 1e-6);
    color = vec4(accumRgb, alphaAccum);
}
