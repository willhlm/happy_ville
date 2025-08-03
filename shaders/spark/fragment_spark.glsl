#version 330 core

uniform vec2 velocity;//to caluclate the angle
uniform vec2 size;//size of the texture: set in init
uniform vec4 colour;// color: set in init
uniform float scale;// size of it

out vec4 fragColor;
in vec2 fragmentTexCoord;// top-left is [0, 1] and bottom-right is [1, 0]

float ndot(vec2 a, vec2 b ) { return a.x*b.x - a.y*b.y; }
float sdRhombus( in vec2 p, in vec2 b )
{
    p = abs(p);
    float h = clamp( ndot(b-2.0*p,b)/dot(b,b), -1.0, 1.0 );
    float d = length( p-0.5*b*vec2(1.0-h,1.0+h) );
    return d * sign( p.x*b.y + p.y*b.x - b.x*b.y );
}

mat2 rotate(float _angle){
    return mat2(cos(_angle),-sin(_angle),sin(_angle),cos(_angle));
}

void main()
{
    vec2 norm_velocity = velocity/sqrt(velocity.x*velocity.x+velocity.y*velocity.y);

    float angle = -1*sign(asin(norm_velocity.y))*acos(norm_velocity.x);
    float SDF = sdRhombus(rotate(angle)*(size*fragmentTexCoord-size*vec2(0.5)), scale*size*vec2(0.40,0.03)); // old: (0.15, 0.05)

    vec4 norm_colour = colour/vec4(255);//normalise
    norm_colour.w = step(SDF,0)*norm_colour.w;

    fragColor = vec4(norm_colour);
}
