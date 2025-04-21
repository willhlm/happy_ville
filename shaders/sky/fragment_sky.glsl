#version 330 core

//https://godotshaders.com/shader/cloudy-skies/

in vec2 fragmentTexCoord;  // Texture coordinates
out vec4 COLOR;

uniform sampler2D imageTexture;  // Texture sampler
uniform float TIME;  // Time

uniform float cloudscale = 1;
uniform float speed = 0.01;
uniform float clouddark = 0.5;
uniform float cloudlight = 0.3;
uniform float cloudcover = 0.2;
uniform float cloudalpha = 3.0;
uniform float skytint = 0.5;
uniform vec4 skycolour1 = vec4(0.2, 0.4, 0.6, 0); // top
uniform vec4 skycolour2 = vec4(0.2, 0.3, 0.3, 0); // bottom
uniform mat2 m = mat2(vec2(1.6, 1.2), vec2(-1.2, 1.6)); // Transformation matrix

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
    float time = TIME * speed * 10.0;

    // Perspective effect based on the y-coordinate (depth effect)
    float perspective = pow(uv.y, 5); // Increase the exponent for a more exaggerated effect
    float parallax_strength = mix(0.2, 1.0, perspective); // Cloud movement based on perspective
    
    // Apply perspective and parallax
    vec2 warped_uv = vec2(uv.x, perspective); 
    warped_uv += vec2(sin(time * 0.1) * 0.1, cos(time * 0.1) * 0.1); // Adding animated turbulence
    
    // Generate cloud density with perspective-based scale
    float q = fbm(warped_uv * cloudscale * 0.5 * fragmentTexCoord.y);
    float r = 0.0;
    float weight = 0.8;
    for (int i = 0; i < 8; i++) {
        r += abs(weight * noise(warped_uv * fragmentTexCoord.y));
        warped_uv = m * warped_uv + time;
        weight *= 0.7;
    }

    // Generate cloud shape with perspective-based scale
    float f = 0.0;
    warped_uv = fragmentTexCoord;
    warped_uv *= cloudscale * fragmentTexCoord.y;  // Adjusting for perspective-based size
    warped_uv += q - time;
    weight = 0.7;
    for (int i = 0; i < 8; i++) {
        f += weight * noise(warped_uv * fragmentTexCoord.y);
        warped_uv = m * warped_uv + time;
        weight *= 0.6;
    }

    f *= r + f;

    // Generate cloud color
    float c = 0.0;
    time = TIME * speed * 2.0;
    warped_uv = fragmentTexCoord;
    warped_uv *= cloudscale * 2.0 * fragmentTexCoord.y;
    warped_uv += q - time;
    weight = 0.4;
    for (int i = 0; i < 7; i++) {
        c += weight * noise(warped_uv * fragmentTexCoord.y);
        warped_uv = m * warped_uv + time;
        weight *= 0.6;
    }

    float c1 = 0.0;
    time = TIME * speed * 3.0;
    warped_uv = fragmentTexCoord;
    warped_uv *= cloudscale * 3.0 * fragmentTexCoord.y;
    warped_uv += q - time;
    weight = 0.4;
    for (int i = 0; i < 7; i++) {
        c1 += abs(weight * noise(warped_uv * fragmentTexCoord.y));
        warped_uv = m * warped_uv + time;
        weight *= 0.6;
    }

    c += c1;

    // Mix sky and cloud colors
    vec4 skycolour = mix(skycolour2, skycolour1, fragmentTexCoord.y);
    vec4 cloudcolour = vec4(1.1, 1.1, 0.9, 1) * clamp((clouddark + cloudlight * c), 0.0, 1.0);
    f = cloudcover + cloudalpha * f * r;
    vec4 result = mix(skycolour, clamp(skytint * skycolour + cloudcolour, 0.0, 1.0), clamp(f + c, 0.0, 1.0));

    COLOR.rgb = result.rgb;
    COLOR.a = result.a;
}
