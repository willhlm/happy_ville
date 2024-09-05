#version 330 core

in vec2 fragmentTexCoord;// holds the Vertex position <-1,+1> !!!
uniform sampler2D imageTexture;// used texture unit
out vec4 COLOR;

uniform float time;

//https://godotshaders.com/shader/simple-energy-shield-2/

uniform vec4 color = vec4(1.0);


float circle(vec2 position, float radius, float feather)
{
	return smoothstep(radius, radius + feather, length(position - vec2(0.5)));
}


void main(){
	
	float outer = circle(vec2(fragmentTexCoord.x, fragmentTexCoord.y), 0.35, 0.01);
	
	float fade_effect = sin(time) * 0.01;
	
	float inner = 1.0 - circle(vec2(fragmentTexCoord.x, fragmentTexCoord.y), 0.275, 0.1 - fade_effect );
	
	COLOR = color;
	COLOR.a -= outer + inner;
	
}