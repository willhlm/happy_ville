#version 330

//https://godotshaders.com/shader/bloom-post-processing-for-viewports/

in vec2 fragmentTexCoord;// holds the Vertex position <-1,+1> !!!
uniform sampler2D imageTexture;// used texture unit
out vec4 COLOR;

uniform float bloomRadius = 1;
uniform float bloomThreshold = 1;
uniform float bloomIntensity = 1;
uniform vec2 TEXTURE_PIXEL_SIZE = vec2(640,340);

vec3 GetBloomPixel(sampler2D tex, vec2 uv, vec2 texPixelSize) {
	vec2 uv2 = floor(uv / texPixelSize) * texPixelSize;
	uv2 += texPixelSize * 0.001;
	vec3 tl = max(texture(tex, uv2).rgb - bloomThreshold, 0.0);
	vec3 tr = max(texture(tex, uv2 + vec2(texPixelSize.x, 0.0)).rgb - bloomThreshold, 0.0);
	vec3 bl = max(texture(tex, uv2 + vec2(0.0, texPixelSize.y)).rgb - bloomThreshold, 0.0);
	vec3 br = max(texture(tex, uv2 + vec2(texPixelSize.x, texPixelSize.y)).rgb - bloomThreshold, 0.0);
	vec2 f = fract( uv / texPixelSize );

	vec3 tA = mix( tl, tr, f.x );
	vec3 tB = mix( bl, br, f.x );

	return mix( tA, tB, f.y );
}

vec3 GetBloom(sampler2D tex, vec2 uv, vec2 texPixelSize) {
	vec3 bloom = vec3(0.0);
	vec2 off = vec2(1) * texPixelSize * bloomRadius;
	bloom += GetBloomPixel(tex, uv + off * vec2(-1, -1), texPixelSize * bloomRadius) * 0.292893;
	bloom += GetBloomPixel(tex, uv + off * vec2(-1, 0), texPixelSize * bloomRadius) * 0.5;
	bloom += GetBloomPixel(tex, uv + off * vec2(-1, 1), texPixelSize * bloomRadius) * 0.292893;
	bloom += GetBloomPixel(tex, uv + off * vec2(0, -1), texPixelSize * bloomRadius) * 0.5;
	bloom += GetBloomPixel(tex, uv + off * vec2(0, 0), texPixelSize * bloomRadius) * 1.0;
	bloom += GetBloomPixel(tex, uv + off * vec2(0, 1), texPixelSize * bloomRadius) * 0.5;
	bloom += GetBloomPixel(tex, uv + off * vec2(1, -1), texPixelSize * bloomRadius) * 0.292893;
	bloom += GetBloomPixel(tex, uv + off * vec2(1, 0), texPixelSize * bloomRadius) * 0.5;
	bloom += GetBloomPixel(tex, uv + off * vec2(1, 1), texPixelSize * bloomRadius) * 0.292893;
	bloom /= 4.171573f;
	return bloom;
}

void main() {
	vec4 col = texture(imageTexture, fragmentTexCoord);
	vec3 bloom = GetBloom(imageTexture, fragmentTexCoord, TEXTURE_PIXEL_SIZE);
	col.rgb += bloom * bloomIntensity;
	COLOR = col;
}
