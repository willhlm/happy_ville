#version 330 core

in vec2 fragmentTexCoord;// top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture;// texture in location 0

out vec4 COLOR;

uniform float vignette_intensity = 1;
uniform float vignette_opacity = 0.1;
uniform vec4 colour = vec4(0.0, 0.0, 0.0, 1);
uniform vec2 u_resolution = vec2(1920.0, 1080.0);  // Screen resolution

float vignette(vec2 uv){
	uv *= 1.0 - uv.xy;
	float vignette = uv.x * uv.y * 15.0;
	return pow(vignette, vignette_intensity * vignette_opacity);
}

void main(){
	vec4 color = texture(imageTexture, fragmentTexCoord);
	vec4 text = vec4 (1,1,1,1);

	text.rgba *= (1.0 - vignette(fragmentTexCoord));

	COLOR = vec4(text.rgb * color.rgb + colour.rgb, text.a * colour.a);
}