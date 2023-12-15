#version 330 core

uniform vec2 p;
uniform vec2 b;
uniform vec2 a;
uniform float w = 1;

uniform vec2 size;//size of the texture: set in init
uniform vec4 colour;// color: set in init

vec4 norm_colour;//store the output here

out vec4 fragColor;
in vec2 fragmentTexCoord;// top-left is [0, 1] and bottom-right is [1, 0]

float sdOrientedVesica( vec2 p, vec2 a, vec2 b, float w )
{
    float r = 0.5*length(b-a);
    float d = 0.5*(r*r-w*w)/w;
    vec2 v = (b-a)/r;
    vec2 c = (b+a)*0.5;
    vec2 q = 0.5*abs(mat2(v.y,v.x,-v.x,v.y)*(p-c));
    vec3 h = (r*q.x<d*(q.y-r)) ? vec3(0.0,r,0.0) : vec3(-d,0.0,d+w);
    return length( q-h.xy) - h.z;
}

void main()
{
    float SDF = sdOrientedVesica(size*fragmentTexCoord, size*a, size*b, w);
    norm_colour = colour/vec4(255);//normalise
    norm_colour.w = step(SDF,0);
    fragColor = vec4(norm_colour);
}
