#version 330

uniform vec2 size;//size of the texture: set in init
uniform int number_particles;//set in init
uniform vec4 colour;// color: set in init
uniform vec2 scale;//set in init
uniform float angle;//set in init

uniform vec2 centers[20];//input
uniform vec2 parallax;//input
uniform vec2 scroll;//input

vec4 norm_color;//store calc here
vec4 out_colour = vec4(0,0,0,0);

in vec2 fragmentTexCoord;//from vertex
out vec4 fragout_colour;

float sdBox( in vec2 p, in vec2 b ){
    vec2 d = abs(p)-b;
    return length(max(d,0.0)) + min(max(d.x,d.y),0.0);
}
mat2 rotate(float _angle){
    return mat2(cos(_angle),-sin(_angle),sin(_angle),cos(_angle));
}

void main(){
  norm_color = colour/vec4(255);
  mat2 rotated = rotate(angle);//outside the loop

  for(int i = 0; i < number_particles; i++){
    vec2 shift = parallax*vec2(-scroll.x,scroll.y);
    vec2 position = centers[i]+shift - size*floor((centers[i]+shift)/size);

    float distance = sdBox(rotated*(fragmentTexCoord * size - position), scale * vec2(0.5,3));
    out_colour += norm_color * step(distance, 0);//change colour
  }
  fragout_colour = vec4(out_colour);
}
