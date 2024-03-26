#version 330 core

in vec2 fragmentTexCoord;
out vec4 color;
uniform sampler2D imageTexture;// texture in location 0

uniform float TIME;

// Wind settings.
uniform float speed = 1.0;
uniform float minStrength = 0.05;
uniform float maxStrength = 0.01;
uniform float strengthScale = 100.0;
uniform float interval = 3.5;
uniform float detail = 1.0;
uniform float distortion = 0.5;
uniform float heightOffset =0.4;
uniform float offset = 0; 

float getWind(vec2 uv, float time) {
    float diff = pow(maxStrength - minStrength, 2.0);
    float strength = clamp(minStrength + diff + sin(time / interval) * diff, minStrength, maxStrength) * strengthScale;
    float wind = (sin(time) + cos(time * detail)) * strength * max(0.0, uv.y -  heightOffset);
    return wind;
}

void main() {
    float time = TIME * speed + offset;
    float wind = getWind(fragmentTexCoord, time);
    vec2 modifiedTexCoord = vec2(fragmentTexCoord.x + wind, fragmentTexCoord.y);
    color = texture(imageTexture, modifiedTexCoord);
}
