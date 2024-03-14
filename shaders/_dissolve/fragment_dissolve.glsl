#version 330 core

//https://godotshaders.com/shader/simple-2d-dissolve/

in vec2 fragmentTexCoord; // top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture; // texture in location 0
out vec4 COLOR;

uniform sampler2D dissolve_texture;
uniform float dissolve_value =0.9;

void main(){
    vec4 main_texture = texture(imageTexture, fragmentTexCoord);
    vec4 noise_texture = texture(dissolve_texture, fragmentTexCoord);
    main_texture.a *= floor(dissolve_value + min(1, noise_texture.x));
    COLOR = main_texture;
}
