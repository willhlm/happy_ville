#version 330 core

in vec2 fragmentTexCoord;// top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture;// ight
uniform sampler2D platform;//recyangle

out vec4 color;

void main()
{
    vec4 lightval = texture(imageTexture,fragmentTexCoord);//light circles
    vec4 background = texture(platform,fragmentTexCoord);//rectangle/platform

    float lightIntensity = dot(lightval.rgb, vec3(1,1,1))*0.333;
    color = vec4(background.xyz * lightval.xyz, background.a  * lightIntensity);;

}
