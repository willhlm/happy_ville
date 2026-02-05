#version 330 core

in vec2 fragmentTexCoord;// top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture;// texture in location 0

out vec4 COLOR;

uniform vec4 original_0;
uniform vec4 original_1;
uniform vec4 original_2;
uniform vec4 original_3;
uniform vec4 original_4;
uniform vec4 replace_0;
uniform vec4 replace_1;
uniform vec4 replace_2;
uniform vec4 replace_3;
uniform vec4 replace_4;

uniform int number_colour;

const float constant = 0.1;

vec4 swap_color(vec4 color){
	vec4 original_colors[5] = vec4[5] (original_0, original_1, original_2, original_3, original_4);
	vec4 replace_colors[5] = vec4[5] (replace_0, replace_1, replace_2, replace_3, replace_4);
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