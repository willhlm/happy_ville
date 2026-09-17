#version 330 core

in vec2 fragmentTexCoord;// top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture;// used texture unit

uniform sampler2D background;
uniform vec4 ambient;

out vec4 color;

void main()
{
    vec3 lightEnergy = max(texture(imageTexture, fragmentTexCoord).rgb, vec3(0.0));
    vec4 scene = texture(background, fragmentTexCoord);

    // Light restores the scene's original colors without washing out dark details.
    vec3 ambientFactor = mix(vec3(1.0), clamp(ambient.rgb, 0.0, 1.0), clamp(ambient.a, 0.0, 1.0));
    vec3 multiplier = ambientFactor + (vec3(1.0) - ambientFactor) * clamp(lightEnergy, 0.0, 1.0);
    color = vec4(scene.rgb * multiplier, scene.a);
}
