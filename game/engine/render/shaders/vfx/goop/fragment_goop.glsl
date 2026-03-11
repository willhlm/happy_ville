#version 330

//https://godotshaders.com/shader/goop-projectile/

in vec2 fragmentTexCoord; // from vertex
out vec4 FragColor;
uniform sampler2D imageTexture;

uniform sampler2D flowMap; // noise
uniform float TIME;
uniform float strength = 0.2; // Strength of the displacement effect
uniform vec2 direction = vec2(0,1); // Direction of displacement flow (set this with GDscript)
uniform vec4 color1 = vec4(0.007843, 1.0, 0.972549, 1.0);
uniform vec4 color2 = vec4(1.0, 1.0, 1.0, 1.0); // Two colors to interpolate between (noise based)

void main() {
  vec4 noise_sample = texture(flowMap, vec2(fragmentTexCoord.x + (TIME * direction.x * -1.0), fragmentTexCoord.y + (TIME * direction.y))); // Sample the noise
	vec4 offset = noise_sample * strength; // Apply strength scalar for a fragmentTexCoord offset
	vec4 texture_check = texture(imageTexture, vec2(fragmentTexCoord.x,fragmentTexCoord.y) + offset.xy - vec2(0.5,0.5)*strength); // Sample the texture using the fragmentTexCoord offset
	vec4 color = mix(color1, color2, noise_sample.x * 1.3); // Sample the two colors
	FragColor = vec4(color.xyz, texture_check.a); // Define final output, using the alpha of the original image
}
