#version 330 core

in vec2 fragmentTexCoord;// top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture;// texture in location 0

uniform vec4 colour; // This is the color uniform
out vec4 FragColor;

void main()
{
    FragColor = vec4(colour/255);//change color

}
