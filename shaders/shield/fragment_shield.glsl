#version 330 core

in vec2 fragmentTexCoord;// holds the Vertex position <-1,+1> !!!
uniform sampler2D imageTexture;// used texture unit
out vec4 COLOR;

//https://godotshaders.com/shader/shield-with-impact-waves/

const float MPI = 1.5707966326;
const int STEPS = 20;
const float LOWER_LIMIT = 0.01;
uniform float zoom_out = 1.0;
uniform float border_decay  = 0.6;
uniform vec4 shield_tint = vec4(0.407843, 0.564706, 0.729412, 0.2);
uniform vec4 shield_saturation = vec4(1., 1., 1., .76);
uniform float attack_angle = 3.14156;
uniform float attack_penetration= 0.2;
uniform float attack_radius  = 0.2;//0.7 when attacked
uniform float attack_amplitude  = 0.03;
uniform float wave_speed  = 16.;
uniform float wave_num  = 17.;
uniform sampler2D noise_texture;
uniform sampler2D screen_tex;
uniform float noise_speed = 3.;
uniform float noise_amplitude  = 0.89;
uniform float noise_deformation  = 6.;
uniform float TIME;

float compute_z_radius(vec2 pos, float r) {
	vec3 o = vec3(pos, -1.);
	return -sqrt(1. - dot(o, o) + (r * r));
}

float compute_front_z(vec2 pos) {
	vec3 p = vec3(pos, -1.);
	return (-sqrt(2. - dot(p, p)));
}

void main() {
	// Sphere computation
	vec2 current_pos = (fragmentTexCoord - 0.5) * (2.0 * zoom_out);
	float len = length(current_pos);
	vec2 attack_direction = vec2(cos(attack_angle), sin(attack_angle));
	vec4 noise_texel = texture(noise_texture, current_pos + TIME * attack_direction * noise_speed);
	vec4 noise_amount = (noise_texel * (1. - noise_amplitude)) + noise_amplitude;
	float noise_mask = (noise_amount.r + noise_amount.g + noise_amount.b) / 3.0;
	float amplitude_decay = (1. + attack_amplitude) * border_decay * noise_mask;
	float border_mask = clamp(len - amplitude_decay, 0., 1. - border_decay) / (1. - border_decay);
	float mask = clamp(ceil(noise_mask * (1. + attack_amplitude) - len), 0., 1.);
	vec4 shield_color = mix(shield_saturation, shield_tint, 1. - border_mask) * mask;
	vec2 deformation_mask = (noise_texel.rg - vec2(.5)) * 2. * mask;

	// Waves
	if(len <= 1. + attack_amplitude) {
		vec2 attack_norm = attack_direction * (1. - attack_penetration);
		vec3 attack_position = vec3(attack_norm, compute_front_z(attack_norm));
		float retained_len = 0.;
		float retained_intensity = 0.;
		float z_step = compute_z_radius(current_pos, 1. + attack_amplitude);
		float hdiff = 1. + attack_amplitude;
		float min_diff = hdiff;
		int step_id = STEPS;
		for(int i = 0; i < STEPS; ++i) {
			vec3 current_projection = vec3(current_pos, z_step);
			vec3 pos_on_surface = normalize(current_projection);
			float att_len = length(attack_position - pos_on_surface);
			if(att_len < attack_radius) {
				float intensity = (cos(att_len * wave_num - TIME * wave_speed) + 1.)/2. * cos((att_len / attack_radius) * MPI);
				hdiff = abs(length(current_projection) - 1. - (intensity * attack_amplitude));
				if(hdiff < min_diff) {
					retained_intensity = intensity;
					retained_len = att_len;
					min_diff = hdiff;
					if (hdiff < LOWER_LIMIT) {
						break;
					}
				}

				float extra = pos_on_surface.z * (1. + (intensity * attack_amplitude));
				z_step += (extra - z_step) * (1. - (float(i) / float(STEPS)));
			} else {
				break;
			}
		}
		if ((hdiff < LOWER_LIMIT) || ((step_id == STEPS) && (min_diff < (1.0 + attack_amplitude)))) {
			float attenuation = cos(((1. - (len / attack_radius))) * MPI);
			shield_color = mask*mix(shield_color, shield_saturation, retained_intensity);
			deformation_mask = mask*mix(current_pos * (1. - retained_intensity), deformation_mask, cos(((1. - (len / attack_radius))) * MPI));
		}
	}

	vec2 texSize = vec2(textureSize(imageTexture, 0)); // Gets shield texture size
	vec2 SCREEN_PIXEL_SIZE = 1.0 / texSize; // Pixel size in shield texture

	vec2 SCREEN_UV = fragmentTexCoord; // Since both textures share the same UV space

	vec4 screen_color = texture(screen_tex, SCREEN_UV + (noise_deformation * deformation_mask * SCREEN_PIXEL_SIZE));
	COLOR = vec4(mix(screen_color.rgb, shield_color.rgb, shield_color.a),  1);
	
}