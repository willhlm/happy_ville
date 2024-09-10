#version 330 core

in vec2 fragmentTexCoord; // Texture coordinates (ranging from [0, 1] in both x and y)
uniform float time;       // Time for animating wind
uniform vec2 velocity;    // Speed of the wind (x for horizontal, y for vertical)
uniform sampler2D noiseTexture; // Noise texture    
uniform vec3 windColor = vec3(1.0);

out vec4 color;

// Function to create a rotation matrix
mat2 getRotationMatrix(float angle)
{
    return mat2(
        cos(angle), -sin(angle),
        sin(angle),  cos(angle)
    );
}

// Function to create a pulsing effect with irregularity
float irregularPulse(float time, float scale)
{
    // Use a combination of sine and noise for irregular pulsing
    float noiseValue = texture(noiseTexture, vec2(time * scale, 0.0)).r;
    float pulseValue = sin(time * scale + noiseValue * 10.0) * 0.5 + 0.5;
    return pulseValue;
}

void main()
{
    // Parameters for wind effect
    float windAmplitude = 0.7;  // Amplitude of the wind lines
    float pulseScale = 0.1;     // Scale for irregular pulse effect

    // Normalize the velocity vector to get direction
    vec2 windDirection = normalize(vec2(-velocity.x, velocity.y));

    // Use atan(y, x) to get the full range of angles (atan2-like behavior)
    float angle = atan(windDirection.y, windDirection.x);  // atan2 version

    // Create a rotation matrix using the angle
    mat2 rotationMatrix = getRotationMatrix(angle);

    // Rotate the texture coordinates for noise sampling
    vec2 rotatedTexCoord = rotationMatrix * (fragmentTexCoord - 0.5) + 0.5;

    // Fetch noise value from the rotated texture coordinates
    float noiseValue = texture(noiseTexture, rotatedTexCoord).r;

    // Calculate wind pattern using the rotated coordinates
    vec2 rotatedVelocity = rotationMatrix * windDirection * length(velocity);
    float windPattern = texture(noiseTexture, rotatedTexCoord + time * rotatedVelocity).r * windAmplitude;

    // Adjust the smoothstep thresholds to make lines more visible
    float lineIntensity = smoothstep(0.3, 1.0, abs(windPattern));

    // Apply the irregular pulsing effect to control line visibility
    //float pulseEffect = irregularPulse(time, pulseScale);

    // Fetch noise value for blending from the rotated coordinates
    //vec3 noiseColor = texture(noiseTexture, rotatedTexCoord).rgb;
    //float noiseIntensity = noiseColor.r; // Use the red channel of the noise texture

    // Blend line intensity with noise intensity and apply pulsing effect
    float finalIntensity = lineIntensity;// * noiseIntensity * pulseEffect;

    // Final color with transparency
    color = vec4(windColor, finalIntensity);
}
