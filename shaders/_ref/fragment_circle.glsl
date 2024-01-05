#version 330

uniform float radius;//in pixels: set in init
uniform vec4 color;// color: set in init
uniform vec2 resolution;//size of the texture: set in init

vec4 norm_color;//store the output here

uniform vec2 position;//from python

out vec4 fragColor;//output

void main() {
  vec2 center = vec2(position.x, resolution.y - position.y);

  float distance = length(gl_FragCoord.xy - center);//in pixels
  norm_color = color/vec4(255);//normalise
  norm_color.w = (1 - length(gl_FragCoord.xy - center)/radius)*step(distance, radius);//make outside to 0
  fragColor = vec4(norm_color);
}
