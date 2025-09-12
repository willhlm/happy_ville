#version 330 core

in vec2 fragmentTexCoord;// holds the Vertex position <-1,+1> !!!
uniform sampler2D imageTexture;// used texture unit
out vec4 COLOR;

//https://godotshaders.com/shader/innovative-zoom-shader/

uniform vec2 zoom_center;
uniform float zoom_amount;
uniform bool keep_within_bounds = true;

void main() {
    // Coordinate UV dell'immagine originale
    vec2 uv = fragmentTexCoord;
    
    // Calcolo delle coordinate UV traslate rispetto al centro dello zoom
    vec2 zoomed_uv = (uv - zoom_center) * zoom_amount + zoom_center;
    
    // Se keep_within_bounds è abilitato, limita le coordinate UV all'intervallo (0-1)
    if (keep_within_bounds) {
        zoomed_uv = clamp(zoomed_uv, vec2(0.0), vec2(1.0));
    }
    
    // Se le coordinate UV traslate sono fuori dai limiti (0-1), imposta il colore del pixel trasparente
    if (zoomed_uv.x < 0.0 || zoomed_uv.x > 1.0 || zoomed_uv.y < 0.0 || zoomed_uv.y > 1.0) {
        COLOR = vec4(0.0, 0.0, 0.0, 0.0);
    } else {
        // Altrimenti, leggi il colore dell'immagine originale alle coordinate UV traslate
        vec2 tex_uv = vec2(zoomed_uv.x, 1.0 - zoomed_uv.y);
        COLOR = textureLod(imageTexture, tex_uv, 0.0);
    }
}