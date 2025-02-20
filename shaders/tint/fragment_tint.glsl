#version 330 core

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;

uniform vec4 colour; // This is the color uniform

out vec4 new_colour;

void main()
{
    new_colour = texture(imageTexture,fragmentTexCoord);//get the texture
    new_colour = mix(new_colour, colour/255, new_colour.a*colour.a/255)*new_colour.a;
}
