#version 330 core

in vec2 fragmentTexCoord;// holds the Vertex position <-1,+1> !!!
uniform sampler2D imageTexture;// used texture unit
out vec4 COLOR;

//https://godotshaders.com/shader/shining-sprite-effect/

uniform float TIME;

const float PI = 3.141516;
uniform float speed = 1.;
uniform vec4 tint = vec4(1., 1., 0., 1.);
uniform float span = 0.3;

float luminance(vec4 colour) {
	return 1.0 - sqrt(0.299*colour.r*colour.r + 0.587*colour.g*colour.g + 0.114*colour.b*colour.b);
}

void main() {
	vec4 colour = texture(imageTexture, fragmentTexCoord);
	float target = abs(sin(TIME * PI * speed) * (1. + span));
	//if(colour.a > 0.) {
		float lum = luminance(colour);
		float diff = abs(lum - target);
		float mx = clamp(1. - diff / span, 0., 1.);
		colour = mix(colour, tint, mx)*colour.a;
	//}

	COLOR = colour;
}
