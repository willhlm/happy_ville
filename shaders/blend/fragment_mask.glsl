#version 330 core

in vec2 fragmentTexCoord;// top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture;// used texture unit

uniform sampler2D background;

out vec4 color;

void main()
{
    vec4 lightval = texture(imageTexture,fragmentTexCoord);//light circle
    vec4 background = texture(background,fragmentTexCoord);//screen

    color = background*lightval;

    //color.xyz = lightval.xyz * (background.xyz * ambient.w + 1 - ambient.w);//background.xyz when ambient = 1, 1 when ambient = 0
    //color.w = lightval.w * background.w;
}
