#version 330 core

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;

uniform vec4 new_colour; // This is the color uniform
uniform vec4 colour; // This is the color uniform
uniform float position; // This is the color uniform

out vec4 out_colour;

void main()
{
    out_colour = mix(colour/255,new_colour/255,position);
    

}
