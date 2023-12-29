#version 330 core

in vec2 fragmentTexCoord;// top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture;// used texture unit

uniform sampler2D background;

out vec4 color;

void main()
{
    vec4 image=texture(imageTexture,fragmentTexCoord);
    vec4 background=texture(background,fragmentTexCoord);

    color.xyz = background.xyz*image.xyz;
    color.w = background.w*image.w*0.75;

}
