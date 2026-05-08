#version 330 core

//precision highp float;

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;
uniform vec2 resolution;
uniform sampler2D normal_map;

uniform vec2 lightPositions[20]; // Assuming up to 20 light sources
uniform float lightRadii[20];     // Corresponding radius for each light source
uniform vec4 colour[20];
uniform vec4 ambient;//texture(imageTexture, fragmentTexCoord); // Get background color

uniform vec2 rectangleCorners[80]; // x/4 is the number of rectangles
uniform int occluder_start_index[20];
uniform int num_rectangle[20];//number of rectangles for each light source
uniform int num_lights;

uniform float angleStart[20];   // Start angle of the cone for each light source
uniform float angleEnd[20];     // End angle of the cone for each light source
uniform float min_radius[20];     // End angle of the cone for each light source

uniform float normal_interact[20];     // if the lightsource should interact with normal map

float diff;
vec3 lightDir;

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
    vec4 backgroundColor = ambient;
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

        float invDistance = inversesqrt(max(distanceToLight2, epsilon));
        vec2 toLight = lightDelta * invDistance;

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
            if (normalTex.a == 0.0) {//if default. not a good solution. not sure how multiple light sources will affect this.
                normal = vec3(toLight, 0.0); // Default normal facing out of the screen
            }

            // Light intensity
            float lightIntensity = max(1.0 - distanceToLight2 / lightRadius2, 0.0);

            lightDir = normalize(vec3(toLight, 0.0));// Calculate the direction from the fragment to the light
            diff = mix(1.0, dot(normal, lightDir), clamp(ambient.a, 0.3, 0.9)* normal_interact[l]);         //smoothstep(0.3, 0.9, ambient.a)   

            // Add light to the background color
            float fade = smoothstep(0.0, 1.0, lightIntensity);
            backgroundColor += vec4(colour[l].xyz *  fade * colour[l].w * diff, lightIntensity * fade * colour[l].w);
        }
    }

    backgroundColor.xyz /= max(mix(backgroundColor.w, 1, ambient.w), epsilon);//normalise the colour, and prevent division by 0        
    color = backgroundColor;
}
