#version 330 core

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;

uniform vec3 colour; // This is the color uniform

out vec4 new_colour;

void main()
{
    new_colour = texture(imageTexture,fragmentTexCoord);//get the texture
    new_colour.xyz = vec3(colour/255);//change color
}
