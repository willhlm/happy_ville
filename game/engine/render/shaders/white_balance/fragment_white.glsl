#version 330 core

in vec2 fragmentTexCoord;// holds the Vertex position <-1,+1> !!!
uniform sampler2D imageTexture;// used texture unit
out vec4 COLOR;

//https://godotshaders.com/shader/white-balance-shader/

uniform vec4 warm_color1 = vec4(0.13, 0, 0.298, 1.0);
uniform vec4 warm_color2 = vec4(0.97, 0.729, 0.149, 1.0);
uniform vec4 cool_color1 = vec4( 0.298,0,0.13, 1.0);
uniform vec4 cool_color2= vec4(0.149, 0.729, 0.97, 1.0);
uniform float temperature = 0.2;

void main() {
    vec4 input_color = textureLod(imageTexture, fragmentTexCoord, 0.0);

    float grayscale_value = dot(input_color.rgb, vec3(0.299, 0.587, 0.114));

    vec3 sampled_color;
    if (temperature > 0.0) {
        vec3 gradient_color = mix(warm_color1.rgb, warm_color2.rgb, grayscale_value);
        sampled_color = vec3(gradient_color);
        COLOR.rgb = mix(input_color.rgb, sampled_color, temperature);
    } else {
        vec3 gradient_color = mix(cool_color1.rgb, cool_color2.rgb, grayscale_value);
        sampled_color = vec3(gradient_color);
        COLOR.rgb = mix(input_color.rgb, sampled_color, -temperature);
    }


    COLOR.a = input_color.a;
}