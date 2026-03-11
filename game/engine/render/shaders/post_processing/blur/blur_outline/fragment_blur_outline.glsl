#version 330 core

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;
uniform float blurRadius;

out vec4 color;

void main()
{
    int kernelSize = int(blurRadius) * 2 + 1;
    vec2 texelSize = 1.0 / textureSize(imageTexture, 0);

    vec4 center = texture(imageTexture, fragmentTexCoord);
    float centerAlpha = center.a;

    bool isOutline = false;
    bool isGlow = false;

    // Check surrounding alpha values
    for(int x = -1; x <= 1; ++x){
        for(int y = -1; y <= 1; ++y){
            if(x == 0 && y == 0) continue;
            vec2 offset = vec2(float(x), float(y)) * texelSize;
            float neighborAlpha = texture(imageTexture, fragmentTexCoord + offset).a;

            // Outline: opaque pixel touching transparent
            if(centerAlpha > 0.0 && neighborAlpha == 0.0)
                isOutline = true;

            // Glow: transparent pixel touching opaque
            if(centerAlpha == 0.0 && neighborAlpha > 0.0)
                isGlow = true;
        }
    }

    // Gaussian kernel weights
    float weights[64];
    float sum = 0.0;
    for(int i = 0; i < kernelSize; ++i){
        float x = float(i) - blurRadius;
        weights[i] = exp(-0.5 * (x * x) / (blurRadius * blurRadius));
        sum += weights[i];
    }
    for(int i = 0; i < kernelSize; ++i){
        weights[i] /= sum;
    }

    // Apply blur if it's an outline
    if(isOutline){
        vec4 blurredColor = vec4(0.0);
        for(int x = -int(blurRadius); x <= int(blurRadius); ++x){
            for(int y = -int(blurRadius); y <= int(blurRadius); ++y){
                vec2 offset = vec2(float(x), float(y)) * texelSize;
                vec4 sample = texture(imageTexture, fragmentTexCoord + offset);
                float w = weights[x + int(blurRadius)] * weights[y + int(blurRadius)];
                blurredColor.rgb += sample.rgb * w * sample.a;
                blurredColor.a += w * sample.a;
            }
        }

        blurredColor.rgb /= max(blurredColor.a, 1e-6);
        color = vec4(blurredColor.rgb, blurredColor.a);
        return;
    }

    // Glow: transparent pixel near visible edge → apply a faded blur color
    if(isGlow){
        vec4 glowColor = vec4(0.0);
        float glowAlpha = 0.0;

        for(int x = -1; x <= 1; ++x){
            for(int y = -1; y <= 1; ++y){
                vec2 offset = vec2(float(x), float(y)) * texelSize;
                vec4 sample = texture(imageTexture, fragmentTexCoord + offset);
                if(sample.a > 0.0){
                    glowColor.rgb += sample.rgb * sample.a;
                    glowAlpha += sample.a;
                }
            }
        }

        if(glowAlpha > 0.0){
            glowColor.rgb /= glowAlpha;
            float fade = 0.1; // glow intensity
            color = vec4(glowColor.rgb, fade * glowAlpha);
        } else {
            color = vec4(0.0);
        }

        return;
    }

    // Default: not an outline or glow → keep original pixel
    color = center;
}
