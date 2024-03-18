#version 330 core

//https://godotshaders.com/shader/simple-2d-dissolve/
//https://godotshaders.com/shader/2d-dissolve-with-burn-edge/

in vec2 fragmentTexCoord; // top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture; // texture in location 0
out vec4 COLOR;

uniform sampler2D dissolve_texture;
uniform float dissolve_value = 0.5;//progress
uniform float burn_size = 0.04;
uniform vec4 burn_color = vec4(1,0,0,1);

void main() {
    vec4 main_texture = texture(imageTexture, fragmentTexCoord);
    vec4 noise_texture = texture(dissolve_texture, fragmentTexCoord);

    // Calculate dissolve threshold and border
    float burn_size_step = burn_size * step(0.001, dissolve_value) * step(dissolve_value, 0.999);
  	float threshold = smoothstep(noise_texture.x-burn_size_step, noise_texture.x, dissolve_value);
  	float border = smoothstep(noise_texture.x, noise_texture.x + burn_size_step, dissolve_value);

  	COLOR.a = threshold*main_texture.a;
  	COLOR.rgb = mix(burn_color.rgb, main_texture.rgb, border);
  }
