#version 330 core

in vec2 fragmentTexCoord;
uniform sampler2D imageTexture;
uniform sampler2D noiseTexture;

uniform vec2 resolution;
uniform vec2 gameResolution = vec2(640.0, 360.0);

// Color configuration
uniform vec3 baseColorRGB = vec3(0.4, 0.7, 0.9);
uniform vec3 coreColorRGB = vec3(0.9, 0.95, 1.0);
uniform vec3 accentColorRGB = vec3(0.7, 0.5, 0.9);

// Animation configuration
uniform float speed = 0.25;
uniform float TIME;

// Size and shape configuration
uniform float sphereSize = 0.3;
uniform float breatheAmount = 0.08;
uniform float breatheSpeed = 1.5;
uniform float borderDistortion = 0.3;
uniform float borderRayCount = 8.0;
uniform float borderRayIntensity = 1.0;

// Star pointer configuration
uniform float starPointCount = 5.0;
uniform float starPointLength = 0.4;
uniform float starPointSharpness = 3.0;
uniform float starPointRotation = 0.0;

// Tendril configuration
uniform float tendrilMinCount = 4.0;
uniform float tendrilMaxCount = 8.0;
uniform float tendrilSharpness = 1.0;
uniform float tendrilLength = 1.0;
uniform float tendrilRotationSpeed = 0.4;
uniform float tendrilWobble = 0.3;

// Particle configuration
uniform float moteCount = 12.0;
uniform float moteSpeed = 1.0;
uniform float moteSize = 0.02;
uniform float orbCount = 10.0;
uniform float orbSpeed = 1.0;
uniform float orbTravelDistance = 0.7;
uniform float orbLifetime = 4.0;

// Effect intensity configuration
uniform float energyIntensity = 0.5;
uniform float coreGlowIntensity = 0.7;
uniform float coreGlowSize = 2.0;
uniform float rimLightIntensity = 0.5;
uniform float outerGlowIntensity = 0.6;
uniform float outerGlowSize = 5.0;
uniform float outerGlowFalloff = 1.0;
uniform float transparency = 0.9;

// Explosion configuration
uniform float explosionProgress = 0.0;
uniform float explosionExpandAmount = 0.8;
uniform float explosionExpandDuration = 0.2;
uniform float explosionDeflateStart = 0.5;
uniform float explosionDeflateDuration = 0.7;
uniform float explosionFlashIntensity = 8.0;
uniform float explosionFlashDuration = 0.3;
uniform float explosionFadeStart = 0.1;

uniform float explosionParticleSpeed = 5.0;
uniform float explosionParticleFadeStart = 0;
uniform float explosionParticleFadeEnd = 0.1;
uniform float explosionBoundaryFadeZone = 0.25;
uniform float explosionMaxMoteDistance = 0.7;
uniform float explosionMaxOrbDistance = 0.7;

// Pixelation configuration
uniform float pixelSize = 1;
uniform float colorSteps = 0;

out vec4 COLOR;

mat2 makem2(in float theta)
{
	float c = cos(theta);
	float s = sin(theta);
	return mat2(c, -s, s, c);
}

float hash2D(vec2 p)
{
	vec3 p3 = fract(vec3(p.xyx) * 0.1031);
	p3 += dot(p3, p3.yzx + 33.33);
	return fract((p3.x + p3.y) * p3.z);
}

float noise(vec2 p)
{
	vec2 i = floor(p);
	vec2 f = fract(p);
	f = f * f * (3.0 - 2.0 * f);
	
	float a = hash2D(i);
	float b = hash2D(i + vec2(1.0, 0.0));
	float c = hash2D(i + vec2(0.0, 1.0));
	float d = hash2D(i + vec2(1.0, 1.0));
	
	return mix(mix(a, b, f.x), mix(c, d, f.x), f.y);
}

float fbm(vec2 p)
{
	float total = 0.0;
	float amp = 0.5;
	
	for (float i = 0.0; i < 5.0; i++)
	{
		total += noise(p) * amp;
		p *= 2.0;
		amp *= 0.5;
	}
	
	return clamp(total, 0.0, 1.0);
}

float hash(float n)
{
	return fract(sin(n) * 43758.5453123);
}

float getStarModifier(float angle)
{
	if (starPointLength <= 0.0 || starPointCount <= 0.0) return 0.0;
	
	float anglePerPoint = 6.28318 / starPointCount;
	float normalizedAngle = mod(angle + starPointRotation, 6.28318);
	float nearestPointAngle = floor(normalizedAngle / anglePerPoint + 0.5) * anglePerPoint;
	float angleFromPoint = abs(normalizedAngle - nearestPointAngle);
	
	float pointShape = 1.0 - smoothstep(0.0, 0.5 / starPointCount, angleFromPoint);
	pointShape = pow(pointShape, starPointSharpness);
	
	return pointShape * starPointLength;
}

void main()
{
	vec2 texCoord = fragmentTexCoord;
	
	float actualPixelSize = (resolution.x / gameResolution.x) * pixelSize;
	vec2 pixelatedCoord = floor(texCoord * resolution / actualPixelSize) * actualPixelSize / resolution;
	texCoord = pixelatedCoord;
	
	vec2 p = (texCoord.xy - 0.5) * 2.0;
	p.x *= resolution.x / resolution.y;
	
	float dist = length(p);
	vec2 pNorm = dist > 0.001 ? p / dist : vec2(0.0);
	float angle = atan(p.y, p.x);
	
	// EXPLOSION EFFECTS
	// Expansion phase: grow quickly
	float expansion = smoothstep(0.0, explosionExpandDuration, explosionProgress) * explosionExpandAmount;
	
	// Deflation phase: shrink after peak
	float deflateEnd = explosionDeflateStart + explosionDeflateDuration;
	float deflation = smoothstep(explosionDeflateStart, deflateEnd, explosionProgress) * explosionExpandAmount;
	
	float explosionExpand = expansion - deflation;  // Net size change
	
	float explosionFade = 1.0 - smoothstep(explosionFadeStart, 1.0, explosionProgress);
	
	// Flash: quick bright burst at start, then gradual dim that overlaps with fade
	float flashPeak = smoothstep(0.0, explosionFlashDuration * 0.2, explosionProgress) * 
	                  (1.0 - smoothstep(explosionFlashDuration * 0.2, explosionFlashDuration * 0.5, explosionProgress));
	float flashLinger = smoothstep(explosionFlashDuration * 0.3, explosionFlashDuration, explosionProgress) *
	                    (1.0 - smoothstep(explosionFadeStart * 0.8, explosionFadeStart * 1.2, explosionProgress));
	float explosionFlash = flashPeak + flashLinger * 0.3;
	
	// Edge fade for containment
	float edgeDistance = 1.0 - dist;
	float textureBoundaryFade = smoothstep(0.0, explosionBoundaryFadeZone, edgeDistance);
	float boundaryFadeAmount = mix(1.0, textureBoundaryFade, explosionProgress);
	
	// Organic boundary
	float breathe = sin(TIME * speed * breatheSpeed) * breatheAmount;
	
	float borderNoise = 0.0;
	int numBorderSamples = int(borderRayCount);
	for (int i = 0; i < 16; i++)
	{
		if (i >= numBorderSamples) break;
		
		float ang = float(i) * 6.28318 / borderRayCount;
		vec2 rotated = pNorm * makem2(ang);
		vec2 samplePos = rotated * 10.0 + vec2(sin(TIME * speed * (0.5 + float(i) * 0.1)), 
		                                        cos(TIME * speed * (0.3 + float(i) * 0.1))) * 2.0 
		                                 + vec2(100.0 + float(i) * 10.0, 200.0 + float(i) * 10.0);
		borderNoise += noise(samplePos) / borderRayCount;
	}
	
	float starMod = getStarModifier(angle);
	float organicRadius = sphereSize + (borderNoise - 0.5) * borderDistortion * borderRayIntensity + breathe + starMod + explosionExpand;
	
	float sphere = smoothstep(organicRadius + 0.2, organicRadius - 0.15, dist);
	
	if (explosionProgress < 0.01 && dist > organicRadius + 0.5) {
		COLOR = vec4(0.0);
		return;
	}
	
	// Energy sampling
	vec2 sphereUV = p * 1.2;
	float energy = 0.0;
	
	for (int i = 0; i < 8; i++)
	{
		float ang = float(i) * 0.7854 + TIME * speed * 0.1;
		vec2 rotatedUV = sphereUV * makem2(ang);
		vec2 flowOffset = vec2(sin(TIME * speed * (0.3 + float(i) * 0.05)),
		                       cos(TIME * speed * (0.2 + float(i) * 0.05))) * 2.0 
		                + 30.0 + float(i) * 5.0;
		energy += fbm(rotatedUV * 1.5 + flowOffset);
	}
	energy *= 0.125 * energyIntensity;
	
	// Detail layers
	vec2 offset1 = vec2(sin(TIME * speed * 0.5), cos(TIME * speed * 0.5)) * 2.0 + 50.0;
	vec2 offset2 = vec2(cos(TIME * speed * 0.6), sin(TIME * speed * 0.55)) * 2.0 + 60.0;
	float detail = (noise((sphereUV * 3.0 + offset1) * 2.0) + noise((sphereUV * 3.0 + offset2) * 2.0)) * 0.5;
	
	// Core glow
	float corePulse = sin(TIME * speed * 3.0) * 0.4 + 0.6;
	corePulse += noise(vec2(sin(TIME * speed * 2.0), cos(TIME * speed * 2.0)) * 2.0 + 60.0) * 0.3;
	float coreGlow = exp(-dist * coreGlowSize) * clamp(corePulse, 0.3, 1.0);
	
	// Fade out core glow during explosion
	coreGlow *= 1.0 - smoothstep(0.0, 0.3, explosionProgress);
	
	// Dynamic tendrils
	float numTendrils = mix(tendrilMinCount, tendrilMaxCount, noise(vec2(TIME * speed * 0.2, 123.45)));
	float rotDir = noise(vec2(TIME * speed * 0.12, 999.99)) > 0.5 ? 1.0 : -1.0;
	float rotSpeed = noise(vec2(TIME * speed * 0.18, 777.77)) * 1.5 + 0.5;
	if (noise(vec2(TIME * speed * 0.08, 333.33)) < 0.2) rotSpeed *= 0.1;
	float baseRotation = TIME * speed * rotDir * rotSpeed * tendrilRotationSpeed;
	
	float tendrils = 0.0;
	if (tendrilLength > 0.0 && numTendrils > 0.0)
	{
		int maxIterations = int(ceil(max(tendrilMinCount, tendrilMaxCount)));
		for (int i = 0; i < 16; i++)
		{
			if (i >= maxIterations) break;
			
			float wobble = sin(TIME * speed * (2.0 + float(i) * 0.3) + float(i) * 2.0) * tendrilWobble;
			wobble += (noise(vec2(TIME * speed * 0.4 + float(i), float(i) * 10.0)) - 0.5) * 0.5;
			
			float ang = float(i) / numTendrils * 6.28318 + baseRotation + wobble;
			float dot_val = max(0.0, dot(pNorm, vec2(cos(ang), sin(ang))));
			float pulse = (sin(TIME * speed * 4.0 + float(i)) * 0.5 + 0.5) * 
			              (noise(vec2(TIME * speed * 3.0 + float(i) * 0.5, float(i) * 15.0)) * 0.5 + 0.5);
			
			float maxReach = organicRadius + tendrilLength * 0.5;
			float lengthFalloff = smoothstep(maxReach, organicRadius * 0.5, dist);
			
			tendrils += pow(dot_val, tendrilSharpness) * lengthFalloff * pulse;
		}
		tendrils = clamp((tendrils / max(numTendrils * 0.5, 1.0)) * (energy * 0.5 + 0.5), 0.0, 0.8);
	}
	
	// Motes
	float motes = 0.0;
	float explosionMoteBoost = explosionProgress * explosionParticleSpeed;
	
	for (float i = 0.0; i < moteCount; i++)
	{
		float explosionOffset = pow(explosionProgress, 1.5) * 1.0;
		vec2 motePos = vec2(sin(TIME * speed * moteSpeed * (1.0 + i * 0.2) + i * 2.0), 
		                    cos(TIME * speed * moteSpeed * (0.8 + i * 0.3) + i * 3.0)) * min(0.3 + explosionOffset, explosionMaxMoteDistance);
		
		float moteFade = 1.0 - smoothstep(explosionParticleFadeStart, explosionParticleFadeEnd, explosionProgress);
		float moteContrib = smoothstep(moteSize + hash(i) * moteSize, 0.0, length(p - motePos)) * moteFade;
		motes += moteContrib * (1.0 + explosionMoteBoost);
	}
	motes = clamp(motes, 0.0, 1.5 + explosionMoteBoost);
	
	// Orbs
	float orbsContribution = 0.0;
	vec3 orbColor = vec3(0.0);
	float explosionOrbSpeed = 1.0 + explosionProgress * explosionParticleSpeed;
	
	for (float i = 0.0; i < orbCount; i++)
	{
		float seed = i * 12.34;
		float orbTime = TIME * speed * orbSpeed * explosionOrbSpeed * (0.6 + hash(seed) * 0.6) + hash(seed + 1.0) * 100.0;
		float lifetime = mod(orbTime, orbLifetime);
		float baseFade = smoothstep(0.0, 0.4, lifetime) * (1.0 - smoothstep(2.5, orbLifetime, lifetime));
		
		float ang = hash(seed + 2.0) * 6.28318;
		float explosionDistanceBoost = 1.0 + pow(explosionProgress, 1.2) * 2.0;
		float orbDistance = min(lifetime * orbTravelDistance * explosionDistanceBoost, explosionMaxOrbDistance);
		vec2 orbPos = vec2(cos(ang), sin(ang)) * orbDistance;
		orbPos += vec2(sin(orbTime * 3.0 + seed) * 0.05, cos(orbTime * 2.5 + seed) * 0.05);
		
		float orbExplosionFade = 1.0 - smoothstep(explosionParticleFadeStart, explosionParticleFadeEnd, explosionProgress);
		float orbSize = (0.03 + hash(seed + 3.0) * 0.04) * (1.0 + explosionProgress * 0.8);
		float orb = smoothstep(orbSize, orbSize * 0.2, length(p - orbPos)) * baseFade * orbExplosionFade;
		
		orbColor += orb * mix(baseColorRGB, accentColorRGB, hash(seed + 4.0)) * (2.0 + explosionProgress * 4.0);
		orbsContribution += orb;
	}
	orbColor = clamp(orbColor, 0.0, 2.0 + explosionProgress * 5.0);
	
	// Final composition
	float intensity = clamp(energy * 0.5 + detail * 0.2, 0.45, 0.75);
	
	vec3 col = mix(baseColorRGB, coreColorRGB, coreGlow * coreGlowIntensity);
	col = mix(col, accentColorRGB, detail * 0.35);
	
	col *= mix(1.0, boundaryFadeAmount, explosionProgress * 0.5);
	
	col += (motes * coreColorRGB * 1.5 + orbColor * 0.8) * boundaryFadeAmount;
	
	if (tendrilLength > 0.0)
	{
		col += tendrils * accentColorRGB * 0.6 * boundaryFadeAmount;
		intensity += tendrils * 0.25;
	}
	
	col *= intensity * 0.6 + 0.4;
	
	col += vec3(explosionFlash * explosionFlashIntensity) * boundaryFadeAmount;
	
	// Rim lighting
	float rimNoise = 0.0;
	for (int i = 0; i < 4; i++)
	{
		vec2 rotated = pNorm * makem2(float(i) * 1.5708);
		rimNoise += noise(rotated * 4.0 + vec2(sin(TIME * speed), cos(TIME * speed)) * 2.0 + 90.0 + float(i) * 20.0);
	}
	float rimLight = pow(1.0 - smoothstep(organicRadius - 0.3, organicRadius + 0.1, dist), 2.0) * 
	       (0.5 + rimNoise * 0.125) * rimLightIntensity;
	col += rimLight * mix(baseColorRGB, accentColorRGB, 0.6) * boundaryFadeAmount;
	
	// Outer glow
	float outerGlow = exp(-max(0.0, dist - organicRadius) * outerGlowSize) * (0.3 + sin(TIME * speed * 4.0) * 0.15 + 0.15) * outerGlowIntensity;
	
	// Fade out outer glow during explosion
	outerGlow *= 1.0 - smoothstep(0.1, 0.4, explosionProgress * outerGlowFalloff);
	
	col = clamp(col + outerGlow * baseColorRGB * boundaryFadeAmount, 0.0, 1.2);
	
	if (colorSteps > 0.0)
	{
		col = floor(col * colorSteps) / colorSteps;
	}
	
	col *= boundaryFadeAmount;
	
	// Alpha
	float edgeFade = smoothstep(organicRadius + 0.3, organicRadius + 0.1, dist);
	
	float alphaBase = sphere * (0.3 + intensity * 0.5) + outerGlow + 0.15 * sphere;
	alphaBase *= edgeFade;
	
	float alphaParticles = motes * 0.25 + clamp(orbsContribution, 0.0, 1.5) * 0.6;
	
	float alpha = alphaBase + alphaParticles;
	
	alpha *= explosionFade;
	alpha *= boundaryFadeAmount;
	
	COLOR = vec4(col, clamp(alpha, 0.0, transparency));
}