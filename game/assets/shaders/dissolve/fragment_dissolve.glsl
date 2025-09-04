#version 330 core

//https://godotshaders.com/shader/simple-2d-dissolve/
//https://godotshaders.com/shader/2d-dissolve-with-burn-edge/

in vec2 fragmentTexCoord; // top-left is [0, 1] and bottom-right is [1, 0]
uniform sampler2D imageTexture; // texture in location 0
out vec4 COLOR;

uniform sampler2D dissolve_texture;
uniform float dissolve_value = 0.5;//progress
uniform float burn_size = 0.1;
uniform vec4 burn_color = vec4(0.6,0.5,0.9,1);

void main() {
    vec4 main_texture = texture(imageTexture, fragmentTexCoord);
    vec4 noise_texture = texture(dissolve_texture, fragmentTexCoord);

    // Ensure burn effect applies properly, avoiding zero burn_size_step
    float burn_size_step = burn_size * step(0.001, dissolve_value) * step(dissolve_value, 0.999);

    // Adjust threshold calculation
    float threshold = smoothstep(noise_texture.x - burn_size_step, noise_texture.x, dissolve_value);

    // Force smooth fade-out when approaching zero
    threshold *= smoothstep(0.0, 0.05, dissolve_value); // Ensures a gradual fade-out at low values

    float border = smoothstep(noise_texture.x, noise_texture.x + burn_size_step, dissolve_value);

    // Apply dissolve effect
    COLOR.a = threshold * main_texture.a;
    COLOR.rgb = mix(burn_color.rgb, main_texture.rgb, border);
}