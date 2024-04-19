#version 330 core

precision highp float;

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;
uniform vec2 resolution;

uniform vec2 lightPositions[2]; // Assuming up to 20 light sources
uniform float lightRadii[2];     // Corresponding radius for each light source
uniform vec4 colour[2];
uniform vec4 ambient;//texture(imageTexture, fragmentTexCoord); // Get background color

uniform vec2 rectangleCorners[8]; // x/4 is the number of rectangles
uniform int num_rectangle;
uniform int num_lights;

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

    for (int l = 0; l < num_lights; l++) { // number of light sources
        vec2 lightPos = lightPositions[l];
        float lightRadius = lightRadii[l];

        // Skip if fragment is too far away from light source
        float distanceToLight = calculateDistance(fragmentTexCoord * resolution, lightPos);
        if (distanceToLight >= lightRadius) {
            continue;
        }

        bool occluded = false;

        for (int r = 0; r < num_rectangle; r++) { // number of rectangles
            vec2[] points = vec2[](
                vec2(rectangleCorners[r * 4].x, resolution.y - rectangleCorners[r * 4].y),
                vec2(rectangleCorners[r * 4 + 1].x, resolution.y - rectangleCorners[r * 4 + 1].y),
                vec2(rectangleCorners[r * 4 + 2].x, resolution.y - rectangleCorners[r * 4 + 2].y),
                vec2(rectangleCorners[r * 4 + 3].x, resolution.y - rectangleCorners[r * 4 + 3].y)
            );

            int n = 4;//number of kanter
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
                break;
                //backgroundColor = vec4(1.0, 0.0, 0.0, 1.0); // No need to check other rectangles if one is occluded
            }
        }

        if (!occluded) {
            // light intensity
            float lightIntensity = max(1.0 - distanceToLight / lightRadius,0);

            // add light together
            float fade = smoothstep(0.0, 0.2, lightIntensity);
            backgroundColor += vec4(colour[l].xyz * lightIntensity * fade * colour[l].w , lightIntensity * fade* colour[l].w);
        }
    }
     backgroundColor.xyz /= mix(backgroundColor.w,1,ambient.w);
    
    // smooth transition for the combined light intensities
    color = vec4(backgroundColor.xyz, backgroundColor.w);
}
