#version 330 core

in vec2 fragmentTexCoord; // Texture coordinates of the current fragment
uniform sampler2D imageTexture; // The base texture

// Outline customization
uniform vec4 outlineColor = vec4(1.0, 1.0, 1.0, 1.0); // Default outline color (white)
uniform float outlineThickness = 5.0; // Thickness of the outline

uniform vec2 resolution = vec2(640, 360); // Screen resolution (for computing pixel size)
uniform float outlineAlphaFalloff = 0; // Control how quickly the outline alpha fades with distance

// Output color
out vec4 COLOR;

// Sobel kernel for edge detection
float edgeDetection(vec2 uv, float thickness) {
    // Compute step sizes for neighboring texels
    float stepX = thickness / resolution.x;
    float stepY = thickness / resolution.y;

    // Sample neighboring texels, clamp coordinates to the [0.0, 1.0] range
    float center = texture(imageTexture, uv).a;

    // Only sample neighbors if within bounds
    float top = texture(imageTexture, clamp(uv + vec2(0.0, stepY), vec2(0.0), vec2(1.0))).a;
    float bottom = texture(imageTexture, clamp(uv - vec2(0.0, stepY), vec2(0.0), vec2(1.0))).a;
    float left = texture(imageTexture, clamp(uv - vec2(stepX, 0.0), vec2(0.0), vec2(1.0))).a;
    float right = texture(imageTexture, clamp(uv + vec2(stepX, 0.0), vec2(0.0), vec2(1.0))).a;

    // Combine to detect edges
    float edges = max(max(abs(center - top), abs(center - bottom)),
                      max(abs(center - left), abs(center - right)));
    return edges;
}

void main() {
    vec2 uv = fragmentTexCoord;

    // Base texture color
    vec4 baseColor = texture(imageTexture, uv);

    // Edge detection
    float edgeValue = edgeDetection(uv, outlineThickness);

    // Determine the outline color
    vec4 finalOutlineColor = outlineColor;

    // Calculate outline position (only draw outline if within bounds)
    bool insideOutlineBounds = uv.x > outlineThickness / resolution.x && uv.x < 1.0 - outlineThickness / resolution.x &&
                               uv.y > outlineThickness / resolution.y && uv.y < 1.0 - outlineThickness / resolution.y;

    // Render logic:

    if (baseColor.a > 0.0) {
        COLOR = baseColor; // Render the base texture color
    } else if (edgeValue > 0.0 && insideOutlineBounds) {
        COLOR = vec4(outlineColor.x, outlineColor.y, outlineColor.z, outlineColor.w * (1.0 - edgeValue * outlineAlphaFalloff) ); // Render the outline if inside bounds
    } else {
        COLOR = vec4(0.0); // Fully transparent
    }
}
