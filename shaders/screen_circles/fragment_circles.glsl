#version 330

uniform vec2 size;//size of the texture: set in init
uniform int number_particles;//set in init
uniform float gradient;//if there should be a gradient: 1 is yes, 0 is no
uniform vec4 colour;// color: set in init

uniform float radius[20];//input
uniform vec2 centers[20];//input

vec4 norm_color;//store calc here
vec4 out_colour = vec4(0,0,0,0);

in vec2 fragmentTexCoord;//from vertex
out vec4 fragout_colour;

void main(){
  norm_color = colour/vec4(255);

  for(int i = 0; i < number_particles; i++){
    float distance = length(fragmentTexCoord * size - centers[i]);//in pixels

    out_colour.xyz += norm_color.xyz * step(distance, radius[i]);//change colour
    out_colour.w += norm_color.w * (1 - gradient * distance/radius[i]) * step(distance,radius[i]);//change alpha.
  }
  fragout_colour = vec4(out_colour);
}
