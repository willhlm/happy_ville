#version 330 core

//precision highp float;

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;
uniform vec2 resolution;
uniform sampler2D normal_map;

uniform vec2 lightPositions[20]; // Assuming up to 20 light sources
uniform float lightRadii[20];     // Corresponding radius for each light source
uniform vec4 colour[20];

uniform vec2 rectangleCorners[80]; // x/4 is the number of rectangles
uniform int occluder_start_index[20];
uniform int num_rectangle[20];//number of rectangles for each light source
uniform int num_lights;

uniform float angleStart[20];   // Start angle of the cone for each light source
uniform float angleEnd[20];     // End angle of the cone for each light source
uniform float min_radius[20];     // End angle of the cone for each light source

uniform float normal_interact[20];     // if the lightsource should interact with normal map
uniform float visibility_fill[20];     // player visibility light, displaced by world light

out vec4 color;

const float epsilon = 1e-6;

bool isOcluded(vec2 p, vec2 q, vec2 pixelCoord, vec2 lightPos){
    vec2 v1 = q - p;
    vec2 v2 = lightPos - pixelCoord;

    float crossProduct = v1.x * v2.y - v1.y * v2.x;
    if (abs(crossProduct) < epsilon) {
        return false;
    }

    float t = (v2.x * (p.y - pixelCoord.y) + v2.y * (pixelCoord.x - p.x)) / crossProduct;
    if (t < 0.0 || t > 1.0) {
        return false; // The intersection point is not between p and q
    }

    float u = (v1.x * (pixelCoord.y - p.y) + v1.y * (p.x - pixelCoord.x)) / -crossProduct;
    if (u < 0.0 || u > 1.0) {
        return false; // The intersection point is not between pixelCoord and lightPos
    }

    return true;
}

void main() {
    vec3 worldUnshaded = vec3(0.0);
    vec3 worldShaded = vec3(0.0);
    vec3 visibilityEnergy = vec3(0.0);
    vec4 normalTex = texture(normal_map, fragmentTexCoord);
    vec2 pixelCoord = fragmentTexCoord * resolution;
    vec3 normal = normalize(normalTex.xyz * 2.0 - 1.0); // Transform normal map color to normal

    for (int l = 0; l < num_lights; l++) { // number of light sources
        vec2 lightPos = lightPositions[l];
        float lightRadius = lightRadii[l];
        float lightRadius2 = lightRadius * lightRadius;
        float minRadius2 = min_radius[l] * min_radius[l];
        vec2 lightDelta = lightPos - pixelCoord;
        float distanceToLight2 = dot(lightDelta, lightDelta);

        if (distanceToLight2 >= lightRadius2 || distanceToLight2 < minRadius2) {
            continue;
        }

        vec2 toLight = distanceToLight2 > epsilon
            ? lightDelta * inversesqrt(distanceToLight2)
            : vec2(0.0, 1.0);

        float start = radians(angleStart[l]); // Define your start angle
        float end = radians(angleEnd[l]); // Define your end angle

        // Skip if fragment is outside the cone region
        float angleToLight = atan(toLight.y, toLight.x)+3.141592;
        if (angleToLight < start || angleToLight > end) {
            continue;
        }

        bool occluded = false;

        for (int r = 0; r < num_rectangle[l]; r++) { // number of rectangles
            int rectIndex = occluder_start_index[l] + r;
            vec2[] points = vec2[](
                vec2(rectangleCorners[rectIndex * 4].x, resolution.y - rectangleCorners[rectIndex * 4].y),
                vec2(rectangleCorners[rectIndex * 4 + 1].x, resolution.y - rectangleCorners[rectIndex * 4 + 1].y),
                vec2(rectangleCorners[rectIndex * 4 + 2].x, resolution.y - rectangleCorners[rectIndex * 4 + 2].y),
                vec2(rectangleCorners[rectIndex * 4 + 3].x, resolution.y - rectangleCorners[rectIndex * 4 + 3].y)
            );

            int n = 4;//number of edges
            // check occlusion for each rectangle
            for (int i = 0; i < n; i++) {
                vec2 p = points[i];
                vec2 q = points[(i + 1) % n];
                if (isOcluded(p, q, pixelCoord, lightPos)) {
                    occluded = true;
                    break;
                }
            }
            if (occluded) {
                break;// No need to check other rectangles if one is occluded
            }
        }

        if (!occluded) {
            float falloff = 1.0 - smoothstep(0.0, lightRadius, sqrt(distanceToLight2));
            vec3 contribution = colour[l].rgb * colour[l].a * falloff;
            if (visibility_fill[l] > 0.5) {
                visibilityEnergy += contribution;
                continue;
            }

            float diffuse = normalTex.a > 0.0 ? max(dot(normal, vec3(toLight, 0.0)), 0.0) : 1.0;
            float normalFactor = mix(1.0, diffuse, clamp(normal_interact[l], 0.0, 1.0));
            worldUnshaded += contribution;
            worldShaded += contribution * normalFactor;
        }
    }

    float worldPeak = max(max(worldUnshaded.r, worldUnshaded.g), worldUnshaded.b);
    float worldReach = clamp(worldPeak, 0.0, 1.0);
    vec3 worldLighting = worldShaded / max(worldPeak, 1.0);
    color = vec4(worldLighting + visibilityEnergy * (1.0 - worldReach), 1.0);
}
