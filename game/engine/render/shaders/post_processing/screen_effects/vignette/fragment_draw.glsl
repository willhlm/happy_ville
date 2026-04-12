#version 330 core

in vec2 fragmentTexCoord;// top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture;// texture in location 0

out vec4 COLOR;

uniform float vignette_intensity = 1;
uniform float vignette_opacity = 0.1;
uniform vec4 colour = vec4(0.0, 0.0, 0.0, 1);

float vignette(vec2 uv){
	uv *= 1.0 - uv.xy;
	float vignette = uv.x * uv.y * 15.0;
	return pow(vignette, vignette_intensity * vignette_opacity);
}

void main(){
	vec4 base = texture(imageTexture, fragmentTexCoord);
	float factor = clamp(vignette(fragmentTexCoord), 0.0, 1.0);
	vec3 mixed = mix(colour.rgb, base.rgb, factor);
	COLOR = vec4(mixed, base.a);
}
