#version 330 core

in vec2 fragmentTexCoord; // top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture; // vignette texture
uniform sampler2D background;   // the screen

out vec4 color;

void main()
{
    // Sample the vignette and background textures
    vec4 vignette = texture(imageTexture, fragmentTexCoord);
    vec4 bg = texture(background, fragmentTexCoord);

    // Invert the vignette alpha to represent lightness, so light areas have higher alpha
    float lightAmount = vignette.a;

    // Blend the light areas with the background using additive blending
    vec3 blendedColor = bg.rgb + lightAmount * vignette.rgb;

    // Ensure the blended color doesn't exceed the maximum color value (clamp to 1.0)
    blendedColor = clamp(blendedColor, 0.0, 1.0);

    // Output the final color, keeping the original background alpha
    color = vec4(blendedColor, bg.a);
}