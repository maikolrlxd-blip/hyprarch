#version 300 es

// hyprarch-crt.frag — ajuste sutil para escritorio SDR (escrito por Codex, revisado por Claude).
// Todas las intensidades están acá. Cero desactiva cada intensidad.

#define SCAN_STRENGTH       0.012
#define SCAN_PERIOD_PX      4.0

#define ENABLE_CA           1
#define CA_PIXELS           0.35
#define CA_EDGE_START       0.55

#define VIGNETTE_STRENGTH   0.055
#define VIGNETTE_START      0.20

#define ENABLE_BLOOM        1
#define BLOOM_STRENGTH      0.080
#define BLOOM_RADIUS_PX     1.5
#define BLOOM_THRESHOLD     0.60
#define BLOOM_FULL          0.90
#define GREEN_DOM_START     0.12
#define GREEN_DOM_FULL      0.45

#define BLACK_DEPTH         0.10
#define SHADOW_TINT         0.012

precision highp float;
precision highp int;

uniform sampler2D tex;
in vec2 v_texcoord;
layout(location = 0) out vec4 fragColor;

vec2 safeUV(vec2 uv, vec2 pixel)
{
    return clamp(uv, 0.5 * pixel, vec2(1.0) - 0.5 * pixel);
}

#if ENABLE_BLOOM
vec3 greenLight(vec3 c)
{
    float dominance = c.g - max(c.r, c.b);
    float selection =
        smoothstep(BLOOM_THRESHOLD, BLOOM_FULL, c.g) *
        smoothstep(GREEN_DOM_START, GREEN_DOM_FULL, dominance);
    return c * selection;
}
#endif

void main()
{
    vec2 pixel = 1.0 / vec2(textureSize(tex, 0));
    vec2 uv = safeUV(v_texcoord, pixel);
    vec4 source = texture(tex, uv);
    vec3 c = source.rgb;
    vec2 p = v_texcoord * 2.0 - 1.0;

#if ENABLE_CA
    float edge = smoothstep(CA_EDGE_START, 1.0, max(abs(p.x), abs(p.y)));
    vec2 shift = p * pixel * CA_PIXELS * edge * edge;
    c.r = texture(tex, safeUV(uv + shift, pixel)).r;
    c.b = texture(tex, safeUV(uv - shift, pixel)).b;
#endif

    float peak = max(c.r, max(c.g, c.b));
    float shadow = 1.0 - clamp(peak, 0.0, 1.0);
    float shadow2 = shadow * shadow;
    c *= 1.0 - BLACK_DEPTH * shadow2;

    float tint = SHADOW_TINT * shadow2;
    c *= vec3(1.0 - 0.5 * tint, 1.0, 1.0 - tint);

#if ENABLE_BLOOM
    vec2 dx = vec2(pixel.x * BLOOM_RADIUS_PX, 0.0);
    vec2 dy = vec2(0.0, pixel.y * BLOOM_RADIUS_PX);
    vec3 glow =
        greenLight(texture(tex, safeUV(uv + dx, pixel)).rgb) +
        greenLight(texture(tex, safeUV(uv - dx, pixel)).rgb) +
        greenLight(texture(tex, safeUV(uv + dy, pixel)).rgb) +
        greenLight(texture(tex, safeUV(uv - dy, pixel)).rgb);
    glow *= 0.25 * BLOOM_STRENGTH;
    c += glow * (vec3(1.0) - c);
#endif

    float phase = fract(gl_FragCoord.y / SCAN_PERIOD_PX);
    float stripe = 1.0 - abs(2.0 * phase - 1.0);
    stripe = stripe * stripe * (3.0 - 2.0 * stripe);
    c *= 1.0 - SCAN_STRENGTH * stripe;

    float radius2 = 0.5 * dot(p, p);
    float vignette = smoothstep(VIGNETTE_START, 1.0, radius2);
    c *= 1.0 - VIGNETTE_STRENGTH * vignette;

    fragColor = vec4(clamp(c, 0.0, 1.0), source.a);
}
