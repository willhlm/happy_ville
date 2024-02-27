#version 330 core

layout(location=0)in vec3 vertexPos;//global position
layout(location=1)in vec2 vertexTexCoord;//vertex position

out vec2 fragmentTexCoord;

void main()
{
    gl_Position=vec4(vertexPos,1.);
    fragmentTexCoord=vertexTexCoord;
}
