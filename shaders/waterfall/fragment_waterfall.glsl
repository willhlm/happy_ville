#version 330 core

//https://godotshaders.com/shader/2d-waterfall/

in vec2 fragmentTexCoord;
out vec4 colour;
uniform sampler2D imageTexture;// texture in location 0

uniform vec2 scale = vec2(1,1); // Used for sprite script. Don't edit this value in the inspector.
uniform float zoom = 1; // Used for sprite script. Don't edit this value in the inspector.

uniform sampler2D refraction_map;
uniform sampler2D water_mask;
uniform sampler2D SCREEN_TEXTURE;
uniform float TIME;

uniform vec2 gap_stretch = vec2(0.8, 0.05);
uniform vec2 refraction_stretch = vec2(2.0, 0.8);
uniform float refraction_strength = 0.02;

uniform vec4 water_tint  = vec4(0.30, 0.45, 0.41, 0.8);
uniform vec4 water_highlight1= vec4(0.38, 0.572, 0.52, 0.8);
uniform vec4 water_highlight2= vec4(0.53,0.70,0.682, 0.8);
uniform vec4 water_highlight3= vec4(0.76,0.85,0.909, 0.8);

uniform float speed = -3;
uniform float flow_gaps = 0;
uniform float highlight_width = 0.1;
uniform vec2 u_resolution = vec2(640, 360);
uniform vec4 section;

// Texture size uniform - pass the actual pixel dimensions of your texture
uniform vec2 texture_size; // Current texture size in pixels
// Reference size for normalization (both speed and scale)
const vec2 reference_size = vec2(300.0, 400.0);

void main()
{
	// Get the two noise textures and make them move on the y axis. The gaps move twice as fast as the refraction, but you can tweak this by changing (speed * 0.5)
    vec2 UV = fragmentTexCoord;
    
    // Calculate normalization factors
    float speed_factor = reference_size.y / texture_size.y; // Use Y dimension for speed (vertical flow)
    float normalized_speed = speed * speed_factor;
    
    // For texture sampling, use a fixed scale based on reference size to make droplets size-independent
    vec2 fixed_scale = reference_size / 500.0; // Adjust this divisor to control base droplet size
    
	vec2 refraction_offset = texture(refraction_map, vec2(UV.x, UV.y + -TIME * normalized_speed * 0.5) * fixed_scale * refraction_stretch).xy;
	vec2 gap_mask = texture(water_mask, vec2(UV.x, UV.y + -TIME * normalized_speed) * fixed_scale * gap_stretch).xy;

	// Set values between -0.5 and 0.5 (instead of 0 and 1). Otherwise the reflection will move whith increased refraction_strength
	//refraction_offset -= 0.5;

    vec2 normalizedSectionPos = vec2(section.x ,section.y)/u_resolution;
	vec2 normalizedSectionSize = vec2(section.z ,section.w)/u_resolution;
	vec2 screenUV = UV * normalizedSectionSize + vec2(normalizedSectionPos.x, 1 - normalizedSectionPos.y - normalizedSectionSize.y);

	// Get the screen texture and distort it
	vec4 refraction = texture(SCREEN_TEXTURE, screenUV + refraction_offset * refraction_strength * zoom);

	// Use the grayscale value of the color to adjust the speed
	float adjustedSpeed = 0.5/(pow(gap_mask.x,0.2)); // Adjust the speed based on the grayscale value
	// Apply the adjusted speed to the gap_mask offset with fixed scale
	gap_mask = texture(water_mask, vec2(UV.x, UV.y + TIME * adjustedSpeed * speed_factor) * fixed_scale * gap_stretch).xy;

	// Create holes and apply colors and textures //
	vec4 color = vec4(1,1,1,1);

	// Define what values will be the water highlight color (the gap border)
	float inner_edge = 1 * (flow_gaps + highlight_width);

    // Check if the pixel is within the edges range and use the water colors alpha to blend between showing color or refraction texture.
	// Compute weights for each range based on gap_mask.x and inner_edge
	float w1 = step(gap_mask.x, 0.2 * inner_edge);
	float w2 = step(0.2 * inner_edge, gap_mask.x) * step(gap_mask.x, 0.7 * inner_edge);
	float w3 = step(0.7 * inner_edge, gap_mask.x) * step(gap_mask.x, 0.8 * inner_edge);
	float w4 = step(0.8 * inner_edge, gap_mask.x);

	// Normalize weights to ensure only one range is active
	vec3 highlightColor = 
		w1 * mix(refraction.rgb, water_highlight1.rgb, water_highlight1.a) +
		w2 * mix(refraction.rgb, water_highlight2.rgb, water_highlight2.a) +
		w3 * mix(refraction.rgb, water_highlight3.rgb, water_highlight3.a) +
		w4 * mix(refraction.rgb, water_tint.rgb, water_tint.a);

	// Assign the resulting color
	color.rgb = highlightColor;
	// Crate Edge Shape //

	// Set the shape for the top and bottom edges. Use water_mask as shape but with other values to flatten it out horizontally.
	// Apply fixed scale to edge animation
	vec2 water_edge = texture(water_mask, vec2(UV.x, UV.y + -TIME * 0.1 * speed_factor) * fixed_scale * vec2(0.15, 0.6)).xy;
	water_edge -= 0.5;

	// Use the same mask as for the gaps for left and right edge.
	vec2 vertical_edge_mask = gap_mask - 0.5;

	// Apply the new masks to the edges. This will make the wobble effect.
	color.a = mix(0.0, color.a, step(UV.x + vertical_edge_mask.x * 0.2, 0.92)); // Right edge
	color.a = mix(color.a, 0.0, step(UV.x - vertical_edge_mask.x * 0.2, 0.08)); // Left edge

	color.a = mix(0.0, color.a, step(UV.y + water_edge.y * 0.03, 0.95));  //top edge
	color.a = mix(color.a, 0.0, step(UV.y - water_edge.y * 0.05, 0.05)); // ottom edge

	// Calculate brightness adjustment based on y-coordinate
	vec3 adjustedColor = color.rgb /pow(1-fragmentTexCoord.y,0);

	// Assign the adjusted color to the final color
	color.rgb =  clamp(adjustedColor, 0.0, 1.0);

	colour =  color;
}