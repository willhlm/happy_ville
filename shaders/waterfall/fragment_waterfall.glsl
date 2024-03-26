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
uniform float refraction_strength = 0.005;//flickers if this is too high

uniform vec4 water_tint  = vec4(0.2, 0.6, 1.0, 0.4);
uniform vec4 water_highlight= vec4(1.0, 1.0, 1.0, 0.3);
uniform float speed = -1.0;
uniform float flow_gaps = 0;
uniform float highlight_width = 0.02;
uniform vec2 u_resolution = vec2(640, 360);
uniform vec4 section;

void main()
{
	// Get the two noise textures and make them move on the y axis. The gaps move twice as fast as the refraction, but you can tweak this by changing (speed * 0.5)
    vec2 UV = fragmentTexCoord;
	vec2 refraction_offset = texture(refraction_map, vec2(UV.x, UV.y + -TIME * speed * 0.5) * scale * refraction_stretch).xy;
	vec2 gap_mask = texture(water_mask, vec2(UV.x, UV.y + -TIME * speed) * scale * gap_stretch).xy;
	
	// Set values between -0.5 and 0.5 (instead of 0 and 1). Otherwise the reflection will move whith increased refraction_strength
	//refraction_offset -= 0.5; 
	
    vec2 normalizedSectionPos = vec2(section.x ,section.y)/u_resolution;
	vec2 normalizedSectionSize = vec2(section.z ,section.w)/u_resolution;
	vec2 screenUV = vec2(fragmentTexCoord.x,fragmentTexCoord.y) * normalizedSectionSize + vec2(normalizedSectionPos.x,1-normalizedSectionPos.y-normalizedSectionSize.y);
	// Get the screen texture and distort it
	vec4 refraction = texture(SCREEN_TEXTURE,screenUV + refraction_offset * refraction_strength * zoom);//replaced screen UV with fragmentTexCoord
	
	// Create holes and apply colors and textures //	
	vec4 color = vec4(1.0);
	
	// Define what values will be the water highlight color (the gap border)
	float inner_edge = flow_gaps + highlight_width;
	
	// See if the pixel is within the edges range and use the water colors alpha to blend between showing color or refraction texture.
	if (gap_mask.x < inner_edge)
	{
		color.rgb = mix(refraction.rgb, water_highlight.rgb, water_highlight.a);
	}
	else
	{
		color.rgb = mix(refraction.rgb, water_tint.rgb, water_tint.a);
	}
	
	// If the value is below the gap threshhold make it transparent (a gap)
	if (gap_mask.x < flow_gaps)
	{
		color.a = 0.0;
	}

	// Crate Edge Shape //
	
	// Set the shape for the top and bottom edges. Use water_mask as shape but with other values to flatten it out horizontally. 
	vec2 water_edge = texture(water_mask, vec2(UV.x, UV.y + -TIME * 0.1) * scale * vec2(0.15, 0.6)).xy;
	water_edge -= 0.5;
	
	// Use the same mask as for the gaps for left and right edge.
	vec2 vertical_edge_mask = gap_mask - 0.5;
	
	// Apply the new masks to the edges. This will make the wobble effect.
	color.a = mix(0.0, color.a, step(UV.x + vertical_edge_mask.x * 0.2, 0.92)); // Right edge
	color.a = mix(color.a, 0.0, step(UV.x - vertical_edge_mask.x * 0.2, 0.08)); // Left edge
	
	color.a = mix(0.0, color.a, step(UV.y + water_edge.y * 0.1, 0.95));  //Bottom edge
	color.a = mix(color.a, 0.0, step(UV.y - water_edge.y * 0.05, 0.05)); //Top edge
	
	colour = color;
}