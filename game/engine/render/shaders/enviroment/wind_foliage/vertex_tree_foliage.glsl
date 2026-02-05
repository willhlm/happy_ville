#version 330 core

layout(location = 0) in vec3 vertexPos;
layout(location = 1) in vec2 vertexTexCoord;

uniform mat4 modelMatrix;

out vec2 fragmentTexCoord;
out vec2 worldPosition;

void main()
{
    gl_Position = vec4(vertexPos, 1.0);
    fragmentTexCoord = vertexTexCoord;
    
    // Calculate world position for noise sampling
    worldPosition = (modelMatrix * vec4(vertexPos.xy, 0.0, 1.0)).xy;
}
