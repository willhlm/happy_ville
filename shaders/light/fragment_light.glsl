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
uniform int num_rectangle[20];//number of rectangles for each light source
uniform int num_lights;

uniform float angleStart[20];   // Start angle of the cone for each light source
uniform float angleEnd[20];     // End angle of the cone for each light source
uniform float min_radius[20];     // End angle of the cone for each light source

out vec4 color;

const float epsilon = 1e-6;

float calculateDistance(vec2 p1, vec2 p2) {
    return sqrt(dot(p1 - p2, p1 - p2));
}

bool isOcluded(vec2 p, vec2 q, vec2 lightPos, float lightRadius) {
    vec2 pixelCoord = fragmentTexCoord * resolution;
    vec2 v1 = q - p;
    vec2 v2 = lightPos - pixelCoord;
    float crossProduct = v1.x * v2.y - v1.y * v2.x;
    float dotProduct = v1.x * v2.x + v1.y * v2.y;
    float lengthV1 = length(v1);
    float lengthV2 = length(v2);
    float t = (v2.x * (p.y - pixelCoord.y) + v2.y * (pixelCoord.x - p.x)) / crossProduct;

    vec2 intersection = p + t * v1;

    if (abs(crossProduct) < epsilon) {
        return false;
    }
    if (distance(p, intersection) > lengthV1 + epsilon || distance(q, intersection) > lengthV1 + epsilon) {
        return false; // The intersection point is not between p and q
    }
    if (distance(pixelCoord, intersection) > lengthV2 + epsilon || distance(lightPos, intersection) > lengthV2 + epsilon) {
        return false; // The intersection point is not between pixelCoord and lightPos
    }
    return true;
}

void main() {
    vec4 backgroundColor = ambient;
    vec3 normal = normalize(texture(normal_map, fragmentTexCoord).xyz * 2.0 - 1.0); // Transform normal map color to normal

    for (int l = 0; l < num_lights; l++) { // number of light sources
        vec2 lightPos = lightPositions[l];
        float lightRadius = lightRadii[l];
        
        float start = radians(angleStart[l]); // Define your start angle
        float end = radians(angleEnd[l]); // Define your end angle

        // Skip if fragment is outside the cone region
        vec2 toLight = normalize(lightPos - fragmentTexCoord * resolution);
        float angleToLight = atan(toLight.y, toLight.x)+3.141592;
        if (angleToLight < start || angleToLight > end) {
            continue;
        }

        // Skip if fragment is too far away from light source
        float distanceToLight = calculateDistance(fragmentTexCoord * resolution, lightPos);
        if (distanceToLight >= lightRadius || distanceToLight < min_radius[l]) {
            continue;
        }

        bool occluded = false;

        for (int r = 0; r < num_rectangle[l]; r++) { // number of rectangles
            vec2[] points = vec2[](
                vec2(rectangleCorners[r * 4].x, resolution.y - rectangleCorners[r * 4].y),
                vec2(rectangleCorners[r * 4 + 1].x, resolution.y - rectangleCorners[r * 4 + 1].y),
                vec2(rectangleCorners[r * 4 + 2].x, resolution.y - rectangleCorners[r * 4 + 2].y),
                vec2(rectangleCorners[r * 4 + 3].x, resolution.y - rectangleCorners[r * 4 + 3].y)
            );

            int n = 4;//number of edges
            // check occlusion for each rectangle
            for (int i = 0; i < n; i++) {
                vec2 p = points[i];
                vec2 q = points[(i + 1) % n];
                if (isOcluded(p, q, lightPos, lightRadius)) {
                    occluded = true;
                    break;
                }
            }
            if (occluded) {
                break;// No need to check other rectangles if one is occluded
            }
        }

       if (!occluded) {
            // Light intensity
            float lightIntensity = max(1.0 - pow(distanceToLight / lightRadius, 2), 0);

            // Calculate the direction from the fragment to the light
            vec3 lightDir = normalize(vec3(lightPos - fragmentTexCoord * resolution, 0.0));
            float diff = max(dot(normal, lightDir), 0.0);

            // Add light to the background color
            float fade = smoothstep(0.0, 1.0, lightIntensity);
            backgroundColor += vec4(colour[l].xyz *  fade * colour[l].w * diff , lightIntensity * fade* colour[l].w);

        }
    }

     backgroundColor.xyz /= max(mix(backgroundColor.w, 1, ambient.w), epsilon);//normalise the colour, and prevent division by 0
        
    // smooth transition for the combined light intensities
    color = backgroundColor;
}
