#version 330 core

in vec2 vertexPos;
in vec2 vertexTexCoord;
in vec2 position;
in vec2 scale;
in float angle;
// <AUTO_VARYINGS_ATTR_IN>
// <AUTO_UVRECT_ATTR_IN>
// <AUTO_VARYINGS_OUT>

out vec2 fragmentTexCoord;

uniform vec2 screenSize;

void main() {
    vec2 local = vertexPos * scale;
    float s = sin(angle);
    float c = cos(angle);
    vec2 rotated = vec2(
        local.x * c - local.y * s,
        local.x * s + local.y * c
    );
    vec2 worldPos = rotated + position;

    vec2 ndc = (worldPos / screenSize) * 2.0 - 1.0;
    ndc.y *= -1.0;
    gl_Position = vec4(ndc, 0.0, 1.0);

    fragmentTexCoord = vertexTexCoord;
    // <AUTO_UVRECT_APPLY>
    // <AUTO_VARYINGS_ASSIGN>
    // <USER_HOOK>
}
