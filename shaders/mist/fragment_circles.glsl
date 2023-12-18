#version 330


uniform vec2 size;//size of the texture: set in init
out vec4 fragColor;
uniform vec2 circles[5];//size of the texture: set in init

void main(){
  vec2 coord = gl_FragCoord.xy / size;
  vec4 color = vec4(0.0,0,0,1);
  vec2 translate = vec2(-0.5, -0.5);
  coord += translate;

  for(int i = 0; i < 5; i++){
    float radius = 0.3;
    float rad = radians(360.0 / 40.0) * float(i);

    color = vec4( length(coord + circles[i]));
    //color.w *= length(coord - circles[i]);

  }

  fragColor = vec4(color);
}
