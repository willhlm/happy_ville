#version 330 core

in vec2 fragmentTexCoord;// top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture;// texture in location 0

uniform vec2 dir = vec2(0.05,0);
uniform int quality = 8;

out vec4 COLOR;

float insideUnitSquare(vec2 v) {
    vec2 s = step(vec2(0.0), v) - step(vec2(1.0), v);
    return s.x * s.y;   
}

void main(){
	float inSquare = insideUnitSquare(fragmentTexCoord);
	float numSamples = inSquare;
	COLOR = texture(imageTexture, fragmentTexCoord) * inSquare;
	vec2 stepSize = dir/(float(quality));
	vec2 uv;
	for(int i = 1; i <= quality; i++){
		uv = fragmentTexCoord + stepSize * float(i);
		inSquare = insideUnitSquare(uv);
		numSamples += inSquare;
		COLOR += texture(imageTexture, uv) * inSquare;
		
		uv = fragmentTexCoord - stepSize * float(i);
		inSquare = insideUnitSquare(uv);
		numSamples += inSquare;
		COLOR += texture(imageTexture, uv) * inSquare;
	}	
	COLOR.xyz /= max(COLOR.w, 1e-6);//prevent division by 0
	COLOR.a /= float(quality)*2.0 + 1.0;
}
