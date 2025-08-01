#version 330 core

layout(location = 0) in vec2 vertexPos;   // now in pixel coords
layout(location = 1) in vec2 vertexTexCoord;

uniform vec2 screenSize; // pass dest_width, dest_height

out vec2 fragmentTexCoord;

void main() {
    // Convert to NDC here
    vec2 ndc = vec2(
        2.0 * vertexPos.x / screenSize.x - 1.0,
        1.0 - 2.0 * vertexPos.y / screenSize.y
    );
    gl_Position = vec4(ndc, 0.0, 1.0);
    fragmentTexCoord = vertexTexCoord;
}
