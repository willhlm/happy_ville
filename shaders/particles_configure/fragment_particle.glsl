#version 330 core

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;
out vec4 colour;

uniform float normalised_frame;
uniform vec4 colour1;
uniform vec4 colour2;
uniform vec4 colour3;


void main(){    
    // Calculate weights for interpolation
    float weight1 = smoothstep(colour1.x, colour2.x, normalised_frame);
    float weight2 = smoothstep(colour2.x, colour3.x, normalised_frame);
    
    // Interpolate between control points
    vec4 color1_2 = mix(colour1, colour2, weight1);
    vec4 color2_3 = mix(colour2, colour3, weight2);
    
    // Final interpolation between interpolated control points
    colour = mix(color1_2, color2_3, normalised_frame) * texture(imageTexture, fragmentTexCoord);
}