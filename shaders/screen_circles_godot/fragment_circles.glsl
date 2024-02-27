#version 330

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;

out vec4 COLOR;

uniform float rain_amount = 100.0;
uniform float near_rain_length = 0.2;
uniform float far_rain_length  = 0.2;
uniform float near_rain_width = 0.4;
uniform float far_rain_width  = 0.4;
uniform float near_rain_transparency  = 1.0;
uniform float far_rain_transparency  = 0.5;

uniform vec4 rain_color  = vec4(0.2, 0.2, 0.8, 1.0);
uniform float base_rain_speed  = -1;
uniform float additional_rain_speed  = 0.5;
uniform float slant  = 0.2;

uniform float TIME;
uniform vec2 size = vec2 (640,360);

void main() {
// To control the rainfall from your program comment out the below line and add a new uniform above as:
// uniform float time = 10000.0;
// Then update the time uniform from your _physics_process function by adding delta. You can then pause the rainfall by not changing the time uniform.
	float time =0.1* TIME;

  vec2 UV = fragmentTexCoord;


// Uncomment the following line if you are applying the shader to a TextureRect and using a version of Godot before 4.
	COLOR = texture(imageTexture,UV);

	vec2 uv = vec2(0.0)*size;
	float remainder = mod(UV.x - UV.y * slant, 1.0 / rain_amount);
	uv.x = (UV.x - UV.y * slant) - remainder;
	float rn = fract(sin(uv.x * rain_amount));
	uv.y = fract((UV.y + rn));

// Blurred trail. Works well for rain:
//	COLOR = mix(COLOR, rain_color, smoothstep(1.0 - (far_rain_length + (near_rain_length - far_rain_length) * rn), 1.0, fract(uv.y - time * (base_rain_speed + additional_rain_speed * rn))) * (far_rain_transparency + (near_rain_transparency - far_rain_transparency) * rn) * step(remainder * rain_amount, far_rain_width + (near_rain_width - far_rain_width) * rn));

// No trail. Works well for snow:
	COLOR = mix(COLOR, rain_color, step(1.0 - (far_rain_length + (near_rain_length - far_rain_length) * rn), fract(uv.y - time * (base_rain_speed + additional_rain_speed * rn))) * (far_rain_transparency + (near_rain_transparency - far_rain_transparency) * rn) * step(remainder * rain_amount, far_rain_width + (near_rain_width - far_rain_width) * rn));
}
