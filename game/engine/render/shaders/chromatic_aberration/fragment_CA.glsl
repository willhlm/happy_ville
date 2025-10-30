#version 330 core

in vec2 fragmentTexCoord;// holds the Vertex position <-1,+1> !!!
uniform sampler2D imageTexture;// used texture unit
out vec4 COLOR;
//https://godotshaders.com/shader/just-chromatic-aberration/

uniform vec2 r_displacement = 2*vec2(6.0, 0.0);
uniform vec2 g_displacement = vec2(0.0, 0.0);
uniform vec2 b_displacement = 2*vec2(-6.0, 0.0);

void main()
{
  vec2 TEXTURE_PIXEL_SIZE = 1.0 / vec2(textureSize(imageTexture, 0).xy);

	float r = texture(imageTexture, fragmentTexCoord + vec2(TEXTURE_PIXEL_SIZE*r_displacement), 0.0).r;
	float g = texture(imageTexture, fragmentTexCoord + vec2(TEXTURE_PIXEL_SIZE*g_displacement), 0.0).g;
	float b = texture(imageTexture, fragmentTexCoord + vec2(TEXTURE_PIXEL_SIZE*b_displacement), 0.0).b;

	vec4 original = texture(imageTexture, fragmentTexCoord, 0.0);
	COLOR = vec4(r, g, b, original.a);

	//COLOR = vec4(r, g, b, 1.0);
}
