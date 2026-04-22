#version 330 core

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;
out vec4 COLOR;

uniform vec4 colour = vec4(0.0, 0.0, 0.0, 0.0);

void main() {
    vec4 base = texture(imageTexture, fragmentTexCoord);
    float overlay_alpha = clamp(colour.a, 0.0, 1.0);
    vec3 out_rgb = mix(base.rgb, colour.rgb, 1 - overlay_alpha);
    float out_alpha = 1.0 - (1.0 - base.a) * overlay_alpha;
    COLOR = vec4(out_rgb, out_alpha);
}
