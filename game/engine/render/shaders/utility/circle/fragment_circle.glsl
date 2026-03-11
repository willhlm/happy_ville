#version 330

uniform vec2 size;//size of the texture: set in init
uniform float radius;//in pixels: set in init
uniform vec4 color;// color: set in init
uniform float gradient;//if there should be a gradient: 1 is yes, 0 is no

vec4 norm_color;//store the output here

in vec2 fragmentTexCoord;//from vertex
out vec4 fragColor;

void main() {
    // Calculate the distance from the center of the circle
    float distance = length(fragmentTexCoord * size - vec2(0.5, 0.5) * size);//in pixels

    // Check if the fragment is inside the circle
    norm_color = color/vec4(255);//normalise
    norm_color.w *= (1 - gradient*distance/radius) * step(distance,radius);//change alpha.
    fragColor = vec4(norm_color);
}
