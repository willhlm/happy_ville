#version 330 core

layout(location = 0) in vec3 vertexPos;
layout(location = 1) in vec2 vertexTexCoord;
layout(location = 2) in vec4 instanceCustom; // Custom per-instance data
layout(location = 3) in int instanceID;      // Instance ID (if needed)

out vec3 fragmentColor;
out vec2 fragmentTexCoord;

// These will be passed to the fragment shader
out float LIFETIME;
out float INDEX;

void main()
{
    // Assign per-instance data
    LIFETIME = instanceCustom.y; // Assuming this is set per-instance
    INDEX = float(instanceID);   // Converting ID to float if needed

    // Standard vertex transformations
    gl_Position = vec4(vertexPos, 1.0);
    fragmentTexCoord = vertexTexCoord;
}
