#version 330 core

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;          // Original texture
uniform sampler2D noiseTexture;          // Perlin noise texture

uniform float baseOutlineWidth = 10.0;   // Base width of the outline in pixels
uniform vec4 colorStart = vec4(0.2, 0.3, 1.0, 1.0); // Starting color of the outline (e.g., blue)
uniform vec4 colorEnd = vec4(0.2, 0.7, 0.7, 1.0);   // Ending color of the outline (e.g., pink)
uniform vec2 screenSize;
uniform float pulse_amplitude = 5;
uniform float TIME;

out vec4 COLOR;

void main() {
    // Calculate pixel size in texture space
    vec2 TEXTURE_PIXEL_SIZE = 1.0 / screenSize;

    // Calculate aspect ratio for the screen
    float aspectRatio = screenSize.x / screenSize.y;

    // Calculate the distances to the edges of the texture in UV space
    float leftDist = fragmentTexCoord.x;
    float rightDist = 1.0 - fragmentTexCoord.x;
    float topDist = fragmentTexCoord.y;
    float bottomDist = 1.0 - fragmentTexCoord.y;

    // Adjust the vertical (y) distance by the aspect ratio to make the outline uniform
    topDist *= aspectRatio;
    bottomDist *= aspectRatio;

    // Find the smallest distance to an edge
    float minDist = min(min(leftDist, rightDist), min(topDist, bottomDist));

    // Convert outline width from pixels to texture space
    float pulse = pulse_amplitude + pulse_amplitude * sin(TIME * 2.0); // Pulse effect for outline thickness
    float outlineWidthUV = (baseOutlineWidth + pulse * 5.0);

    // Sample Perlin noise to modulate the outline thickness or color
    float noiseValue = texture(noiseTexture, fragmentTexCoord * 0.05 + vec2(TIME * 0.1, 0.0)).r; // Use time for animation
    float noiseFactor = (noiseValue * 0.5 + 0.5);  // Normalize the noise value to range [0.0, 1.0]

    // Calculate a smooth gradient for magical color effect
    vec4 outlineColor = mix(colorStart, colorEnd, sin(TIME + minDist * 10.0) * 0.5 + 0.5);

    // Apply the outline effect with glow
    float fadeFactor = smoothstep(0.0, outlineWidthUV * (1.0 + noiseFactor), minDist);  // Modulate with noise factor

    // Blend the outline color with a glowing effect
    vec4 glowColor = mix(outlineColor, vec4(outlineColor.rgb * 1.5, 1.0), 1.0 - fadeFactor);

    // Final color mixing with the texture
    COLOR = mix(glowColor, texture(imageTexture, fragmentTexCoord), fadeFactor);
}
