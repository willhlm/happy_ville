#version 330 core

in vec2 fragmentTexCoord;
out vec4 color;

uniform int numStops; // Number of color stops
uniform float offsets[10]; // Up to 10 offsets (must be in ascending order)
uniform vec3 colors[10];  // Up to 10 colors

uniform bool isVertical = true; // false = horizontal, true = vertical

void main() {
    float t = isVertical ? fragmentTexCoord.y : fragmentTexCoord.x;

    // Default to the first color
    vec3 finalColor = colors[0];

    for (int i = 0; i < numStops - 1; i++) {
        float startOffset = offsets[i];
        float endOffset = offsets[i + 1];

        if (t >= startOffset && t <= endOffset) {
            float localT = (t - startOffset) / (endOffset - startOffset); // Normalize
            finalColor = mix(colors[i], colors[i + 1], localT); // Interpolate
            break;
        }
    }

    color = vec4(finalColor, 1.0);
}
