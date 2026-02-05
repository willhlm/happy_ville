#version 330 core

out vec4 fragColor;
in vec2 fragmentTexCoord;// top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture;// used texture unit

uniform float progress = 0;
uniform float noise_desnity = 20;
uniform float beam_size = 0.1;
uniform vec4 color  = vec4(0, 1, 1, 1.0);

// We are generating our own noise here. You could experiment with the
// built in SimplexNoise or your own noise texture for other effects.
vec2 random(vec2 uv){
    uv = vec2( dot(uv, vec2(127.1,311.7) ),
               dot(uv, vec2(269.5,183.3) ) );
    return -1.0 + 2.0 * fract(sin(uv) * 43758.5453123);
}

float noise(vec2 uv) {
    vec2 uv_index = floor(uv);
    vec2 uv_fract = fract(uv);

    vec2 blur = smoothstep(0.0, 1.0, uv_fract);

    return mix( mix( dot( random(uv_index + vec2(0.0,0.0) ), uv_fract - vec2(0.0,0.0) ),
                     dot( random(uv_index + vec2(1.0,0.0) ), uv_fract - vec2(1.0,0.0) ), blur.x),
                mix( dot( random(uv_index + vec2(0.0,1.0) ), uv_fract - vec2(0.0,1.0) ),
                     dot( random(uv_index + vec2(1.0,1.0) ), uv_fract - vec2(1.0,1.0) ), blur.x), blur.y) * 0.5 + 0.5;
}

void main()
{
  vec2 UV = fragmentTexCoord;
	vec4 tex = texture(imageTexture, UV);

	float noise = noise(UV * noise_desnity) * UV.y;

	float d1 = step(progress, noise);
	float d2 = step(progress - beam_size, noise);

	vec3 beam = vec3(d2 - d1) * color.rgb;

	tex.rgb += beam;
	tex.a *= d2;

	fragColor = tex;
}
