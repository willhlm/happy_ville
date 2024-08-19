#version 330 core

layout(location = 0) in vec2 aPos;
layout(location = 1) in vec2 aTexCoord;
layout(location = 2) in vec3 aNormal;

out vec2 fragmentTexCoord;
out vec3 fragNormal;

uniform mat4 modelMatrix;  // Character's model transformation matrix
uniform mat4 viewMatrix;
uniform mat4 projectionMatrix;

void main() {
    gl_Position = projectionMatrix * viewMatrix * modelMatrix * vec4(aPos, 0.0, 1.0);
    fragmentTexCoord = aTexCoord;
    
    // Transform the normal to world space
    vec3 normal = normalize((modelMatrix * vec4(aNormal, 0.0)).xyz);
    fragNormal = normal;
}