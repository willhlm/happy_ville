#version 330

in vec2 vertexPos;

in vec2 instPos;
in vec2 instScale;
in float instRot;
in float instCustom;

out vec2 texCoord;
out float custom;

uniform vec2 screenSize;

void main() {
    float s = sin(instRot);
    float c = cos(instRot);

    vec2 rotated = vec2(
        vertexPos.x * c - vertexPos.y * s,
        vertexPos.x * s + vertexPos.y * c
    );

    vec2 worldPos = instPos + rotated * instScale;
    vec2 clipPos = (worldPos / screenSize) * 2.0 - 1.0;

    gl_Position = vec4(clipPos * vec2(1, -1), 0.0, 1.0);

    texCoord = vertexPos + vec2(0.5);  // range: [0.0, 1.0]
    custom = instCustom;
}
