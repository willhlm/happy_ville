#version 330 core

in vec2 fragmentTexCoord;// top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture;// used texture unit

uniform sampler2D background;

uniform vec4 ambient;

out vec4 color;

void main()
{
    vec4 lightval=texture(imageTexture,fragmentTexCoord);
    vec4 background=texture(background,fragmentTexCoord);
    vec4 norm_ambient = ambient/1;
    color.xyz = background.xyz*(norm_ambient.xyz+lightval.xyz);
    color.w = 2*background.w*(norm_ambient.w*lightval.w);//2 is needed to remove the boundaries

}
