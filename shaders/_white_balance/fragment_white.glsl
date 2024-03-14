#version 330 core

in vec2 fragmentTexCoord;// holds the Vertex position <-1,+1> !!!
uniform sampler2D imageTexture;// used texture unit
out vec4 COLOR;

//https://godotshaders.com/shader/white-balance-shader/

uniform sampler2D warm_color;
uniform sampler2D cool_color;
uniform float temperature = 0;

void main(){

	vec4 input_color = textureLod(imageTexture, fragmentTexCoord, 0.0);

	float grayscale_value = dot(input_color.rgb, vec3(0.299, 0.587, 0.114));
	vec3 sampled_color;
	if (temperature > 0.0){
		sampled_color = texture(warm_color, vec2(grayscale_value, 0.0)).rgb;
		COLOR.rgb = mix(input_color.rgb, sampled_color, temperature);
	}
	else{
		sampled_color = texture(cool_color, vec2(grayscale_value, 0.0)).rgb;
		COLOR.rgb = mix(input_color.rgb, sampled_color, temperature * -1.0);
	}
	COLOR.a = input_color.a;
}
