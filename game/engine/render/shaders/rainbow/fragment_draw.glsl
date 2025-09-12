#version 330 core

in vec2 fragmentTexCoord; // top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture; // texture in location 0

out vec4 COLOR;

uniform vec2 center = vec2(0.5, 0.1);  // Move the center to the top (change Y coordinate to 0.1 or any smaller value)
uniform float radius = 0.6;
uniform float width = 0.3;
uniform float transparency = 0.6;
// If applying the shader to a ColorRect:
uniform vec2 dimensions = vec2(640.0, 360.0); // ColorRect dimensions in pixels.

// Define the rainbow colors (RGB values)
vec3 red = vec3(1.0, 0.0, 0.0);
vec3 orange = vec3(1.0, 0.5, 0.0);
vec3 yellow = vec3(1.0, 1.0, 0.0);
vec3 green = vec3(0.0, 1.0, 0.0);
vec3 blue = vec3(0.0, 0.0, 1.0);
vec3 indigo = vec3(0.29, 0.0, 0.51);
vec3 violet = vec3(0.93, 0.51, 0.93);

// Function to blend between two colors
vec3 mixColors(vec3 color1, vec3 color2, float t) {
    return mix(color1, color2, t);
}

// Function to determine the color at a given position in the rainbow
vec3 getRainbowColor(float hue) {
    // Normalize hue value to the range [0.0, 1.0]
    float t = hue / 360.0;

    vec3 color = mix(violet, indigo, smoothstep(0.0, 1.0, t));            // Violet to Indigo
    color = mix(color, blue, smoothstep(1.0 / 6.0, 2.0 / 6.0, t));         // Indigo to Blue
    color = mix(color, green, smoothstep(2.0 / 6.0, 3.0 / 6.0, t));        // Blue to Green
    color = mix(color, yellow, smoothstep(3.0 / 6.0, 4.0 / 6.0, t));       // Green to Yellow
    color = mix(color, orange, smoothstep(4.0 / 6.0, 5.0 / 6.0, t));       // Yellow to Orange
    color = mix(color, red, smoothstep(5.0 / 6.0, 1.0, t));               // Orange to Red

    return color;
}

void main() {
    // Adjust aspect ratio
    vec2 aspect_ratio = vec2(dimensions.x / dimensions.y, 1.0);
    vec2 uv = fragmentTexCoord * aspect_ratio;

    // Compute the distance from the center of the circle
    float d = length(uv - center * aspect_ratio);

    // Map the distance d to a hue value for the rainbow (0.0 to 360.0 degrees)
    float hue = (d - radius + width / 2.0) / width * 360.0;

    // Ensure hue stays within the range [0, 360]
    hue = mod(hue, 360.0);

    // Get the rainbow color based on the hue
    vec3 rainbowColor = getRainbowColor(hue);

    // Create a smooth alpha transition for the rainbow boundary
    float alpha = smoothstep(radius + width * 0.5, radius, d) * smoothstep(radius - width / 2.0, radius + width / 2.0, d) * transparency;
    
    // Set the final color with the smooth transition and alpha
    COLOR = vec4(rainbowColor, alpha);
}
