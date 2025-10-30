#version 330 core

in vec2 fragmentTexCoord;
out vec4 colour;

uniform vec2 scale=vec2(1,1); // Used for sprite script. Don't edit this value in the inspector.
uniform float zoom=10; // Used for sprite script. Don't edit this value in the inspector.

uniform sampler2D refraction_map;//noise
uniform sampler2D water_mask;//noise
uniform sampler2D SCREEN_TEXTURE;
uniform float TIME;
uniform vec2 SCREEN_UV = vec2(640,360);

uniform vec2 gap_stretch = vec2(0.8, 0.05);
uniform vec2 refraction_stretch = vec2(2.0, 0.8);
uniform float refraction_strength = 0.005;

uniform vec4 water_tint = vec4(0.2, 0.6, 1.0, 0.7);//water colour
uniform vec4 water_highlight = vec4(1.0, 1.0, 1.0, 1);//"water texture colour"
uniform float speed = -1.0;
uniform float flow_gaps = 0.001;//how much gap
uniform float highlight_width = 0.02;//width of the "water texture"

void main()
{
    vec2 UV = fragmentTexCoord;
    vec2 refraction_offset = texture(refraction_map, vec2(UV.x, UV.y + -TIME * speed * 0.5) * scale * refraction_stretch).xy;
    vec2 gap_mask = texture(water_mask, vec2(UV.x, UV.y + -TIME * speed) * scale * gap_stretch).xy;

    refraction_offset -= 0.5;

    vec4 refraction =texture(SCREEN_TEXTURE, SCREEN_UV - refraction_offset * refraction_strength * zoom);

    vec4 color;

    float inner_edge = flow_gaps + highlight_width;

    if (gap_mask.x < inner_edge)
    {
        color = mix(refraction, water_highlight, water_highlight.a); // Blend with water_highlight color
    }
    else
    {
        color = mix(refraction, water_tint, water_tint.a); // Blend with water_tint color
    }

    if (gap_mask.x < flow_gaps)
    {
        color.a = 0.0;
    }

    vec2 water_edge = texture(water_mask, vec2(UV.x, UV.y + -TIME * 0.1) * scale * vec2(0.15, 0.6)).xy;
    water_edge -= 0.5;

    vec2 vertical_edge_mask = gap_mask - 0.5;

    color.a = mix(0.0, color.a, step(UV.x + vertical_edge_mask.x * 0.2, 0.92));
    color.a = mix(color.a, 0.0, step(UV.x - vertical_edge_mask.x * 0.2, 0.08));

    color.a = mix(0.0, color.a, step(UV.y + water_edge.y * 0.1, 0.95));
    color.a = mix(color.a, 0.0, step(UV.y - water_edge.y * 0.05, 0.05));

    colour = color;
}
