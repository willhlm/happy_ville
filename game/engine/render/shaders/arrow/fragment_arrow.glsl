#version 330 core

in vec2 fragmentTexCoord; // Top-left is [0, 1], bottom-right is [1, 0]
uniform sampler2D imageTexture; // Texture for moon's surface
uniform vec2 iResolution = vec2(640, 360); // Resolution of the viewport
uniform vec4 moonColor = vec4(1.0, 1.0, 1.0, 1.0); // Moon base color with alpha
uniform vec2 moonDirection = vec2(0, -1.0); // Moon direction (pointing direction)
uniform float radiusA = 0.4; // Radius of the main circle (moon shape)
uniform float radiusB = 0.43; // Radius of the subtractive circle (moon phase)
uniform float phase = 0; // Moon phase (0 = new moon, 1 = full moon)
uniform float pointiness = 0.6; // Controls how "pointy" the moon is
uniform float TIME = 0.0; // Animation time

out vec4 COLOR;

// Signed Distance Function for the moon
float sdMoon(vec2 p, float d, float ra, float rb) {
    p.y = abs(p.y) + pointiness * pow(p.x, 2.0); // Adjust pointiness
    float a = (ra * ra - rb * rb + d * d) / (2.0 * d);
    float b = sqrt(max(ra * ra - a * a, 0.0));
    if (d * (p.x * b - p.y * a) > d * d * max(b - p.y, 0.0))
        return length(p - vec2(a, b));
    return max(
        (length(p) - ra),
        -(length(p - vec2(d, 0)) - rb)
    );
}

void main() {
    vec2 uv = fragmentTexCoord * iResolution / min(iResolution.x, iResolution.y);
    vec2 center = vec2(0.5, 0.5); // Moon's center in normalized coordinates

    // Rotate moon direction
    float angle = atan(moonDirection.y, moonDirection.x); // Keep original direction
    mat2 rotation = mat2(cos(angle), -sin(angle), sin(angle), cos(angle));
    vec2 rotatedP = rotation * (uv - center);

    // Invert the X direction after rotation
    rotatedP.x = -rotatedP.x;

    // Invert the Y direction after rotation (adjust for OpenGL coordinates)
    rotatedP.y = -rotatedP.y;

    // Dynamic moon phase
    float distanceBetweenCenters = mix(0.1, radiusA * 2.0, phase);

    // Calculate the moon's alpha using the signed distance function
    float alpha = 1.0 - smoothstep(0.0, 0.005, sdMoon(rotatedP, distanceBetweenCenters, radiusA, radiusB));

    // Dynamic color animation
    vec3 dynamicColor = mix(vec3(1.0, 0.8, 0.6), vec3(0.8, 0.6, 1.0), 0.5 + 0.5 * sin(TIME));
    vec4 baseMoonColor = vec4(dynamicColor, moonColor.a);

    // Add subtle texture for moon surface
    vec2 moonTexCoord = rotatedP / radiusA * 0.5 + 0.5; // Map texture to moon area
    float craterNoise = texture(imageTexture, moonTexCoord).r; // Sample texture
    vec4 texturedMoonColor = mix(baseMoonColor, baseMoonColor * 0.7, craterNoise * alpha); // Blend craters

    // Calculate alpha for moon only (without any glow or aurora)
    COLOR = texturedMoonColor; // Just output the moon texture color

    COLOR.a *= alpha; // Apply alpha transparency based on SDF
}