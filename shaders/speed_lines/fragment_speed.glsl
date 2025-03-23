#version 330 core

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;
out vec4 COLOR;

uniform float TIME;
uniform sampler2D noise;

uniform float line_count = 3;
uniform float line_density = 0.4;
uniform float line_faloff = 0.25;
uniform float mask_size = 0.04;
uniform float mask_edge = 0.5;
uniform float animation_speed = 1;
uniform vec4 line_color = vec4(1,1,1,1);

uniform vec2 center = vec2(0.5,0.5); // Define center as a uniform vec2, 0,0 is bottom left, 1,1 is topright

float inv_lerp(float from, float to, float value){
  return (value - from) / (to - from);
}

vec2 polar_coordinates(vec2 uv, vec2 center, float zoom, float repeat){
    vec2 dir = uv - center;
    float radius = length(dir) * 2.0;
    float angle = atan(dir.y, dir.x) * 1.0/(3.141592 * 2.0);
    return mod(vec2(radius * zoom, angle * repeat), 1.0);
}

vec2 rotate_uv(vec2 uv, vec2 pivot, float rotation) {
    float cosa = cos(rotation);
    float sina = sin(rotation);
    uv -= pivot;
    return vec2(
        cosa * uv.x - sina * uv.y,
        cosa * uv.y + sina * uv.x 
    ) + pivot;
}

void main(){
    vec2 UV = fragmentTexCoord;
    vec2 center_screen = vec2(center.x, 1- center.y);
    vec2 polar_uv = polar_coordinates(rotate_uv(UV, center_screen, floor(fract(TIME) * animation_speed) ) , center_screen, 0.01, line_count); // Use center as reference position
    vec3 lines = texture(noise, polar_uv).rgb;
    
    float mask_value = length(UV - center_screen); // Use center as reference position
    float mask = inv_lerp(mask_size, mask_edge, mask_value);
    float result = 1.0 - (mask * line_density);
    
    result = smoothstep(result, result + line_faloff, lines.r);
    
    COLOR.rgb = vec3(line_color.rgb);
    COLOR.a = min(line_color.a, result);
}