#version 330 core

in vec2 fragmentTexCoord;// top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture;// texture in location 0

uniform float ratio = 0;
uniform float power = 5;
uniform float min_speed = 0;
uniform float max_speed = 0;

out vec4 COLOR;

void main()
{
    vec2 uv = fragmentTexCoord;

    uv*= 2.0;
    uv -= vec2(1.0);
    float len = length(uv);
    float rspeed = mix(max_speed, min_speed, len);

    float sinx = sin((1. - ratio)*rspeed );
    float cosx = cos((1. - ratio)*rspeed );

    vec2 trs = uv * mat2(vec2(cosx, sinx), vec2(-sinx,cosx));
    trs /= pow(ratio, power);

    trs += vec2(1.0);
    trs /= 2.;
    if (trs.x > 1. || trs.x < 0. || trs.y  > 1. ||  trs.y < 0. ){

        COLOR = vec4(0.);

    } else{
        vec4 col = texture(imageTexture, trs);
        COLOR = col;
    }

}

