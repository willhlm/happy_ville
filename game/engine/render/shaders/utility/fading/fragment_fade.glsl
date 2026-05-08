#version 330 core

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;

uniform sampler2D mask_texture;
uniform float threshold = 0.0;
uniform float feather = 0.02;
uniform bool invert = false;

out vec4 COLOR;

void main() {
    vec4 base = texture(imageTexture, fragmentTexCoord);
    vec4 mask_sample = texture(mask_texture, fragmentTexCoord);
    float luminance = dot(mask_sample.rgb, vec3(0.2126, 0.7152, 0.0722));
    float visibility = smoothstep(threshold - feather, threshold + feather, luminance);

    if (invert) {
        visibility = 1.0 - visibility;
    }

    COLOR = vec4(base.rgb, base.a * visibility);
}
