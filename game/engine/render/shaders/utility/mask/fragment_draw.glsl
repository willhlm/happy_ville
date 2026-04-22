#version 330 core

in vec2 fragmentTexCoord;// top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture;// texture in location 0
uniform sampler2D maskTexture;
uniform vec4 maskColour = vec4(0.0, 0.0, 0.0, 1.0);

out vec4 color;

void main()
{
    vec4 base = texture(imageTexture, fragmentTexCoord);
    vec4 mask = texture(maskTexture, fragmentTexCoord);
    color = mix(base, vec4(maskColour.rgb, base.a), mask.a);
}
