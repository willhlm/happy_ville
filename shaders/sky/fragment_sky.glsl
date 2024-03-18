#version 330 core

in vec2 fragmentTexCoord;  // Texture coordinates
out vec4 COLOR;

uniform sampler2D imageTexture;  // Texture sampler
uniform float TIME;  // Time

uniform float cloudscale = 4;
uniform float speed = 0.01;
uniform float clouddark = 0.5;
uniform float cloudlight = 0.3;
uniform float cloudcover = 0.2;
uniform float cloudalpha = 3.0;
uniform float skytint = 0.5;
uniform vec4 skycolour1 = vec4(0.2, 0.4, 0.6,1);//top
uniform vec4 skycolour2 = vec4(0.2, 0.3, 0.3,1);//bottom
uniform mat2 m = mat2(vec2(1.6,1.2),vec2(-1.2,1.6)); // Transformation matrix

// Functions

vec2 hash(vec2 p) {
    p = vec2(dot(p, vec2(127.1, 311.7)), dot(p, vec2(269.5, 183.3)));
    return -1.0 + 2.0 * fract(sin(p) * 43758.5453123);
}

float noise(vec2 p) {
    float K1 = 0.366025404;  // (sqrt(3)-1)/2;
    float K2 = 0.211324865;  // (3-sqrt(3))/6;
    vec2 i = floor(p + (p.x + p.y) * K1);
    vec2 a = p - i + (i.x + i.y) * K2;
    vec2 o = (a.x > a.y) ? vec2(1.0, 0.0) : vec2(0.0, 1.0);
    vec2 b = a - o + K2;
    vec2 c = a - 1.0 + 2.0 * K2;
    vec3 h = max(0.5 - vec3(dot(a, a), dot(b, b), dot(c, c)), 0.0);
    vec3 n = h * h * h * h * vec3(dot(a, hash(i + 0.0)), dot(b, hash(i + o)), dot(c, hash(i + 1.0)));
    return dot(n, vec3(70.0));
}

float fbm(vec2 n) {
    float total = 0.0, amplitude = 0.1;
    for (int i = 0; i < 7; i++) {
        total += noise(n) * amplitude;
        n = m * n;
        amplitude *= 0.4;
    }
    return total;
}

void main() {
    vec2 uv = fragmentTexCoord; // Use fragmentTexCoord directly
    float time = TIME * speed*10;

    // Generate cloud density
    float q = fbm(uv * cloudscale * 0.5*fragmentTexCoord.y);
    float r = 0.0;
    float weight = 0.8;
    for (int i = 0; i < 8; i++) {
        r += abs(weight * noise(uv*fragmentTexCoord.y));
        uv = m * uv + time;
        weight *= 0.7;
    }

    // Generate cloud shape
    float f = 0.0;
    uv = fragmentTexCoord;
    uv *= cloudscale*fragmentTexCoord.y;
    uv += q - time;
    weight = 0.7;
    for (int i = 0; i < 8; i++) {
        f += weight * noise(uv*fragmentTexCoord.y);
        uv = m * uv + time;
        weight *= 0.6;
    }

    f *= r + f;

    // Generate cloud color
    float c = 0.0;
    time = TIME * speed * 2.0;
    uv = fragmentTexCoord;
    uv *= cloudscale * 2.0*fragmentTexCoord.y;
    uv += q - time;
    weight = 0.4;
    for (int i = 0; i < 7; i++) {
        c += weight * noise(uv*fragmentTexCoord.y);
        uv = m * uv + time;
        weight *= 0.6;
    }

    float c1 = 0.0;
    time = TIME * speed * 3.0;
    uv = fragmentTexCoord;
    uv *= cloudscale * 3.0*fragmentTexCoord.y;
    uv += q - time;
    weight = 0.4;
    for (int i = 0; i < 7; i++) {
        c1 += abs(weight * noise(uv*fragmentTexCoord.y));
        uv = m * uv + time;
        weight *= 0.6;
    }

    c += c1;

    // Mix sky and cloud colors
    vec4 skycolour = mix(skycolour2, skycolour1, fragmentTexCoord.y);
    vec4 cloudcolour = vec4(1.1, 1.1, 0.9,1) * clamp((clouddark + cloudlight * c), 0.0, 1.0);
    f = cloudcover + cloudalpha * f * r;
    vec4 result = mix(skycolour, clamp(skytint * skycolour + cloudcolour, 0.0, 1.0), clamp(f + c, 0.0, 1.0));

    COLOR.rgb = result.rgb;
    COLOR.a=result.a;
}
