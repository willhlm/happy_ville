#version 330 core

in vec2 fragmentTexCoord;// top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture;// texture in location 0

out vec4 COLOR;

uniform float vignette_intensity = 1;
uniform float vignette_opacity = 0.15;
uniform vec4 vignette_rgb = vec4(0.0, 0.0, 0.0, 1);

float vignette(vec2 uv){
	uv *= 1.0 - uv.xy;
	float vignette = uv.x * uv.y * 15.0;
	return pow(vignette, vignette_intensity * vignette_opacity);
}

void main(){
  vec2 UV = fragmentTexCoord;
	vec4 color = texture(imageTexture, UV);
	vec4 text = vec4 (1,1,1,1);

	text.rgba *= (vignette_rgb.rgba);
	text.rgba *= (1.0 - vignette(UV));

	COLOR = vec4((text.rgb)*color.rgb,text.a);
}

//this version works to change the colour
//void main() {
  //  vec2 UV = fragmentTexCoord;
    //vec4 color = texture(imageTexture, UV);

    // Calculate vignette factor and invert it
    //float vignetteFactor = 1.0 - vignette(UV);

    // Apply vignette color and blend with texture color
    //vec4 vignetteColor = vignette_rgb * vignetteFactor;
    //COLOR = mix(color, vignetteColor, vignetteFactor);
//}
