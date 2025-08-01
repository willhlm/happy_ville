#version 330 core

//https://godotshaders.com/shader/input-ouput/

in vec2 fragmentTexCoord; // holds the Vertex position <-1,+1> !!!
uniform sampler2D imageTexture; // used texture unit
uniform float TIME;
out vec4 COLOR;

uniform float aspect = 3.0;
uniform vec2 size = vec2(2);
uniform float radius = 0.05; //0.01
uniform float speed = 0.7;
uniform float ySpread = 1.6;
uniform int numBlocks = 70;
uniform float basePulse = 0.33;
uniform vec4 color1 = vec4(0.0, 0.3, 0.6, 1);
uniform vec4 color2 = vec4(0.0, 0.3, 0.6, 1);

float rand(float x)
{
    return fract(sin(x) * 4358.5453123);
}

float rand2(vec2 co)
{
    return fract(sin(dot(co.xy, vec2(12.9898, 78.233))) * 43758.5357);
}

float pulseColor()
{
    float myPulse = basePulse + sin(TIME) * 0.1;
    return myPulse < 1.0 ? myPulse : 1.0;
}

float box(vec2 p, vec2 b, float r)
{
    return length(p) - r;
}

void main()
{
    float pulse = pulseColor();

    vec2 uv = fragmentTexCoord - 0.5;
    vec4 baseColor = color1;

    vec4 color = vec4(0, 0, 0, 0); //pulse*baseColor*0.5*(0.9);
    uv.x *= aspect;

    for (int i = 0; i < numBlocks; i++)
    {
        float z = 1.0 - 0.7 * rand(float(i) * 1.4333); // 0=far, 1=near
        float tickTime = TIME * z * speed + float(i) * 1.23753;
        float tick = floor(tickTime);

        vec2 pos = vec2(0.6 * aspect * (rand(tick) - 0.5), ySpread * (0.5 - fract(tickTime))); // Modified line

        //vec2 size = 1.8*z*vec2(0.04, 0.04 + 0.1*rand(tick+0.2));
        float b = box(uv - pos, size, radius);
        float dust = z * smoothstep(0.22, 0.0, b) * pulse * 0.5;
        float block = 0.2 * z * smoothstep(0.002, 0.0, b);
        float shine = 0.6 * z * pulse * smoothstep(-0.002, b, 0.007);
        color += dust * baseColor + block * z + shine;
    }

    color -= rand2(uv) * 0.04;
    COLOR = vec4(color);
}