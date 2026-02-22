#version 330 core

in vec2 fragmentTexCoord;
in vec4 tint;
in float glow;

uniform sampler2D imageTexture;
uniform float time;

out vec4 color;

const float SCALE_GLOW = .2f;
const float SCALE_TIME = .005f;

void main()
{
    color = texture(imageTexture, fragmentTexCoord) * tint;
    float timeGlow = (sin(time * SCALE_TIME) + 1.0) * glow;
    color += timeGlow * glow * vec4(1, 1, 0, 0);
}
