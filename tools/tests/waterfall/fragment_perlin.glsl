#version 330 core

precision mediump float;

uniform float u_time;
uniform vec2 u_resolution;
float scale = 100;
uniform vec2 shift;

out vec4 colour;
in vec2 fragmentTexCoord;

vec2 randomGradient(vec2 p) {
  p = p + 0.02;
  float x = dot(p, vec2(123.4, 234.5));
  float y = dot(p, vec2(234.5, 345.6));
  vec2 gradient = vec2(x, y);
  gradient = sin(gradient);
  gradient = gradient * 43758.5453;

  // part 4.5 - update noise function with time
  gradient = sin(gradient + u_time);
  return gradient;
}

vec2 quintic(vec2 p) {
  return p * p * p * (10.0 + p * (-15.0 + 6.0 * p));
}

void main() {
  // part 0 - basic shader setup
  vec2 translateUV = shift / (u_resolution);
  vec2 uv = (fragmentTexCoord + translateUV*100) / u_resolution;
  //vec2 uv = (fragmentTexCoord.xy+shift) / u_resolution;

  vec3 black = vec3(0.0);
  vec3 white = vec3(1.0);
  vec3 color = black;

  // part 1 - set up a grid of cells
  uv = uv * u_resolution * scale;
  vec2 gridId = floor(uv);
  vec2 gridUv = fract(uv);
  color = vec3(gridUv, 0.0);

  // part 2.1 - start by finding the coords of grid corners
  vec2 bl = mod(gridId, scale);
  vec2 br = mod(gridId + vec2(1.0, 0.0), scale);
  vec2 tl = mod(gridId + vec2(0.0, 1.0), scale);
  vec2 tr = mod(gridId + vec2(1.0, 1.0), scale);

  // part 2.2 - find random gradient for each grid corner
  vec2 gradBl = randomGradient(bl);
  vec2 gradBr = randomGradient(br);
  vec2 gradTl = randomGradient(tl);
  vec2 gradTr = randomGradient(tr);

  // part 3.2 - find distance from current pixel to each grid corner
  vec2 distFromPixelToBl = gridUv - vec2(0.0, 0.0);
  vec2 distFromPixelToBr = gridUv - vec2(1.0, 0.0);
  vec2 distFromPixelToTl = gridUv - vec2(0.0, 1.0);
  vec2 distFromPixelToTr = gridUv - vec2(1.0, 1.0);

  // part 4.1 - calculate the dot products of gradients + distances
  float dotBl = dot(gradBl, distFromPixelToBl);
  float dotBr = dot(gradBr, distFromPixelToBr);
  float dotTl = dot(gradTl, distFromPixelToTl);
  float dotTr = dot(gradTr, distFromPixelToTr);

  // part 4.4 - smooth out gridUvs
  gridUv = quintic(gridUv);

  // part 4.2 - perform linear interpolation between 4 dot products
  float b = mix(dotBl, dotBr, gridUv.x);
  float t = mix(dotTl, dotTr, gridUv.x);
  float perlin = mix(b, t, gridUv.y);

  // part 4.3 - display perlin noise
  color = vec3(perlin + 0.2);

  colour = vec4(color, 1.0);
}
