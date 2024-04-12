#version 330 core

in vec2 fragmentTexCoord; // top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture; // texture in location 0
out vec4 COLOR;

uniform sampler2D noise;
uniform float TIME;

uniform float speed = 0.3;
uniform float size = 0.08;

uniform vec2 u_resolution; // screen size
uniform vec2 center = vec2(0.5, 0.5); // Center of the distortion
uniform float radius = 1; // Distance threshold from the center to apply distortion
uniform vec3 tint = vec3(1,1,1);
uniform bool shine = false;


//shining
const float PI = 3.141516;
uniform float speed_shine = 1.;
uniform float span = 0.3;

float shining(vec3 colour) {
	return 1.0 - sqrt(0.299*colour.r*colour.r + 0.587*colour.g*colour.g + 0.114*colour.b*colour.b);
}

void main() {
    vec2 offset = fragmentTexCoord - vec2(center.x / u_resolution.x, 1 - center.y / u_resolution.y);
    float distanceFromCenter = length(offset);
    
    // Calculate the step function for the distance comparison 
    float withinThreshold = 1 - smoothstep(radius * 0.5, radius * 0.5 + radius*0.5, distanceFromCenter);
    
    // Apply distortion only if within the threshold distance
    vec2 smoke_uv = fragmentTexCoord + TIME * speed * withinThreshold;//*size
    vec4 smoke_color = texture(noise, fract(smoke_uv));
    smoke_color = clamp(smoke_color * size * withinThreshold*distanceFromCenter*distanceFromCenter, 0.0, 1.0);
    
    vec4 img_color = texture(imageTexture, fragmentTexCoord + vec2(smoke_color.g - size*distanceFromCenter*distanceFromCenter / 2.0, 0.0));
    
    // Convert img_color to grayscale
    float luminance = dot(img_color.rgb, vec3(0.299, 0.587, 0.114));
    img_color.rgb = vec3(luminance)*tint;

    if (shine){//same code as shining shader. Need to put it here if we want shining only when inside the portal
        float target = abs(sin(TIME * PI * speed_shine) * (1. + span));
        //if(colour.a > 0.) {
        float lum = shining(img_color.rgb);
        float diff = abs(lum - target);
        float mx = clamp(1. - diff / span, 0., 1.);
        img_color.rgb = mix(img_color.xyz, tint, mx)*img_color.a;	
    }

    // Mix between distorted and original color based on the step function result
    COLOR = mix(texture(imageTexture, fragmentTexCoord), img_color, withinThreshold);
}