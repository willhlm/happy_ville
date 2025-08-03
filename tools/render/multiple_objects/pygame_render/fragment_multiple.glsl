#version 330

in vec2 texCoord;
in float custom;  // <- Needed to avoid mismatch

uniform sampler2D tex;

out vec4 fragColor;

void main() {
    vec4 color = texture(tex, texCoord);
    fragColor = color;
}
