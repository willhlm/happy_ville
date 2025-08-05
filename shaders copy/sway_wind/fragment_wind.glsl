#version 330 core

in vec2 fragmentTexCoord;
out vec4 color;
uniform sampler2D imageTexture;// texture in location 0

uniform float TIME;

// Wind settings.
uniform float speed = 0.01;
uniform float minStrength = 0.01;
uniform float maxStrength = 0.05;
uniform float strengthScale = 13.0;
uniform float interval = 3.5;
uniform float detail = 1.0;
uniform float distortion = 0.5;
uniform float heightOffset = 0.1;
uniform float offset = 0; //offset in time
uniform float upsidedown = 1;//one is upsidedown, 0 is no

float getWind(vec2 uv, float time) {
    float diff = pow(maxStrength - minStrength, 2.0);
    float strength = clamp(minStrength + diff + sin(time / interval) * diff, minStrength, maxStrength) * strengthScale;
    float wind = (sin(time) + cos(time * detail)) * strength * max(0.0, (1 - upsidedown)*uv.y + upsidedown*(upsidedown - uv.y) -  heightOffset);
    return wind;
}

void main() {
    float time = TIME * speed + offset;
    float wind = getWind(fragmentTexCoord, time);
    vec2 modifiedTexCoord = vec2(fragmentTexCoord.x + wind, fragmentTexCoord.y);
    color = texture(imageTexture, modifiedTexCoord);
}