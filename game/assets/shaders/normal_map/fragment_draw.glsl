#version 330 core

in vec2 fragmentTexCoord; // Texture coordinate passed from vertex shader
uniform sampler2D imageTexture; // Texture in location 0
uniform float direction; // 1.0 for right, -1.0 for left

out vec4 color;

void main()
{
    // Sample the normal map texture
    vec4 texColor = texture(imageTexture, fragmentTexCoord);

    // Convert texture color to normal
    // Assuming the normal map uses [0,1] range where 0.5 is the neutral normal direction
    vec3 normal = texColor.rgb * 2.0 - 1.0;

    // Invert the x-direction if direction is negative
    normal.x *= sign(direction);

    // Convert normal back to texture color space
    vec3 modifiedColor = (normal + 1.0) / 2.0;

    // Output the modified color
    color = vec4(modifiedColor, texColor.a);
}
