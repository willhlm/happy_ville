#version 330 core

in vec2 fragmentTexCoord; // Texture coordinates (ranging from [0, 1] in both x and y)
uniform float time;       // Time for animating wind
uniform vec2 velocity;    // Speed of the wind (x for horizontal, y for vertical)
uniform sampler2D noiseTexture; // Noise texture    
uniform vec3 windColor = vec3(1.0);
uniform float lifetime;   // Lifetime for fading out

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

    // Gradually increase the transparency based on the time (fade-in)
    float timeTransparency = smoothstep(0.0, 1.0, time * 0.4);  // Adjust factor for timing

    // Fade out based on lifetime (fade-out)
    // We assume lifetime is normalized from 0 to 1 (1 = full lifetime, 0 = expired)
    float lifetimeTransparency = smoothstep(0.0, 50, lifetime);

    // Combine both fade-in (time) and fade-out (lifetime) transparency
    float finalTransparency = timeTransparency * lifetimeTransparency;

    // Apply the irregular pulsing effect to control line visibility
    //float pulseEffect = irregularPulse(time, pulseScale);

    // Final color with combined transparency effects
    color = vec4(windColor, lineIntensity * finalTransparency);
}
