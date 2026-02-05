#version 330 core

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;
out vec4 COLOR;

uniform int pixel_size= 3;

void main(){
  vec2 TEXTURE_PIXEL_SIZE = 1.0 / vec2(textureSize(imageTexture, 0).xy);

	vec2 pos = fragmentTexCoord / TEXTURE_PIXEL_SIZE;
	vec2 square = vec2(float(pixel_size), float(pixel_size));
	vec2 top_left = floor(pos / square) * square;
	vec4 total = vec4(0., 0., 0., 0.);
	for (int x = int(top_left.x); x < int(top_left.x) + pixel_size; x++){
		for (int y = int(top_left.y); y < int(top_left.y) + pixel_size; y++){
			total += texture(imageTexture, vec2(float(x), float(y)) * TEXTURE_PIXEL_SIZE);
		}
	}
	COLOR = total / float(pixel_size * pixel_size);
}
