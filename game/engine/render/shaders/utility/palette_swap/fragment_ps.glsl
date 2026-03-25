#version 330 core

in vec2 fragmentTexCoord;// top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture;// texture in location 0

out vec4 COLOR;

uniform int number_colour;
uniform vec4 original_colors[32];
uniform vec4 replace_colors[32];

const float constant = 0.01;

vec4 swap_color(vec4 color){
	for (int i = 0; i < number_colour; i ++) {
		if (distance(color, original_colors[i]/255) <= constant){
			return replace_colors[i]/255;
		}
	}
	return color;
}

void main() {
	COLOR = swap_color(texture(imageTexture, fragmentTexCoord));
}
