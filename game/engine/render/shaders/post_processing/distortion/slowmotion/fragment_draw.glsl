#version 330 core

in vec2 fragmentTexCoord; // [0,1] UV coordinates

uniform vec2 resolution;
uniform vec2 u_resolution;
uniform vec4 section;

out vec4 COLOR;

uniform float progress  = 0.0;

uniform float strength = 0.08;
uniform vec2 center = vec2(0.5, 0.5);

uniform float aberration = 0.425;
uniform float width =  0.04;
uniform float feather = 0.135;

uniform sampler2D SCREEN_TEXTURE;


void main() {

	vec2 sample_st = fragmentTexCoord;
	vec2 st = vec2(fragmentTexCoord.x, 1.0 - fragmentTexCoord.y);

	float aspect_ratio = resolution.y / resolution.x;

	vec2 scaled_st = (st - vec2(0.0, 0.5)) / vec2(1.0, aspect_ratio) + vec2(0.0, 0.5);

	vec2 scaled_min = (vec2(0.0) - vec2(0.0, 0.5)) / vec2(1.0, aspect_ratio) + vec2(0.0, 0.5);
	vec2 scaled_max = (vec2(1.0) - vec2(0.0, 0.5)) / vec2(1.0, aspect_ratio) + vec2(0.0, 0.5);
	float max_radius = min(
		min(center.x - scaled_min.x, scaled_max.x - center.x),
		min(center.y - scaled_min.y, scaled_max.y - center.y)
	);

	float radius = progress * max_radius * 0.8;

	vec2 dist_center = scaled_st - center;

	float dist = length(dist_center);

	float mask = (1.0 - smoothstep(radius - feather, radius, dist)) *
				 smoothstep(radius - width - feather, radius - width, dist);

	// prevent ring appearing when progress = 0
	float activation = smoothstep(0.001, 0.02, progress);
	mask *= activation;

	vec2 dir = dist > 0.0001 ? dist_center / dist : vec2(0.0);
	vec2 offset = dir * strength * mask;

	vec2 biased_st = scaled_st - offset;

	vec2 abber_vec = offset * aberration * mask;

	vec2 final_st = clamp(sample_st * (1.0 - mask) + vec2(biased_st.x, 1.0 - biased_st.y) * mask, 0.0, 1.0);
	vec2 sample_offset = clamp(abber_vec, vec2(-1.0), vec2(1.0));
	vec2 normalized_section_pos = vec2(section.x, section.y) / u_resolution;
	vec2 normalized_section_size = vec2(section.z, section.w) / u_resolution;
	vec2 section_origin = vec2(normalized_section_pos.x, 1.0 - normalized_section_pos.y - normalized_section_size.y);

	vec2 screen_final_st = final_st * normalized_section_size + section_origin;
	vec2 texture_offset = vec2(
		sample_offset.x * normalized_section_size.x,
		-sample_offset.y * normalized_section_size.y
	);

	vec4 red = texture(SCREEN_TEXTURE, clamp(screen_final_st + texture_offset, 0.0, 1.0));
	vec4 blue = texture(SCREEN_TEXTURE, clamp(screen_final_st - texture_offset, 0.0, 1.0));
	vec4 ori = texture(SCREEN_TEXTURE, screen_final_st);

	vec4 distorted = vec4(red.r, ori.g, blue.b, 1.0);

	// inner invert mask
	float inner_mask = (1.0 - smoothstep(radius, radius + feather, dist)) * activation;
	float alpha = max(mask, inner_mask);

	vec4 inverted = vec4(1.0 - ori.rgb, 1.0);

	COLOR = vec4(mix(distorted.rgb, inverted.rgb, inner_mask), alpha);
}
