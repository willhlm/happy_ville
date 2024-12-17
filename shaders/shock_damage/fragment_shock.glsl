#version 330

in vec2 fragmentTexCoord; // Holds the vertex position (texture coordinate)
uniform sampler2D imageTexture; // Texture unit for the image
out vec4 COLOR; // Output color

// Shock effect parameters
uniform float amplitude = 0.05;  // Initial amplitude of the shock effect (scaled down for better visibility)
uniform float frequency = 100.0;  // Frequency of the shock effect (slower oscillations)
uniform vec4 colour = vec4(1,1,1,1);  // Shock color (white in this case)
uniform float time;  // Time variable (equivalent to TIME in the original)
uniform float decay_rate = 10;  // Decay rate of the amplitude over time (higher value = faster decay)
uniform vec2 direction=vec2(1,0);
void main() {
    // Apply exponential decay to the amplitude over time
    float dampedAmplitude = amplitude * exp(-decay_rate * time);

    // Create a sine wave offset based on time, frequency, and damped amplitude
    float sineOffset = dampedAmplitude * sin(frequency * time);  // Time-based sine offset

    // Adjust the fragment texture coordinate based on the sine wave offset
    vec2 disturbedTexCoord = fragmentTexCoord + vec2(direction.x*sineOffset, direction.y*sineOffset);  // Disturb only along x-axis

    // Fetch the color from the texture at the disturbed coordinate
    vec4 original = texture(imageTexture, disturbedTexCoord);

    // Set the output color to the specified shock color (e.g., white)
    COLOR.rgb = mix(original.rgb,  colour.rgb, colour.a);  // Set the color to white (or another color if you wish)
    COLOR.a = original.a;  // Preserve the original alpha channel
}
