#version 330 core
//https://godotshaders.com/shader/2d-fog-overlay-2/

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;

out vec4 COLOR = vec4(1,1,1,1);
uniform float TIME;

uniform sampler2D noise_texture;
// Fog density
uniform float density = 1;
// Fog speed
uniform vec2 speed = vec2(0.02, 0.01);


// Called for every pixel the material is visible on
void main() {
	// Make the fog slowly move
	vec2 uv = fragmentTexCoord + speed * TIME;
	// Sample the noise texture
	float noise = texture(noise_texture, uv).r;
	// Convert the noise from the (0.0, 1.0) range to the (-1.0, 1.0) range
	// and clamp it between 0.0 and 1.0 again
	float fog = clamp(noise * 2.0 - 1.0, 0.0, 1.0);
	// Apply the fog effect
	COLOR.a *= fog * density;
}