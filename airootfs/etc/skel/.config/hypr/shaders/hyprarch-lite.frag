#version 300 es

// hyprarch-lite.frag — solamente contraste y viñeta, para escritorio SDR.

#define BLACK_DEPTH         0.10
#define VIGNETTE_STRENGTH   0.055
#define VIGNETTE_START      0.20

precision highp float;

uniform sampler2D tex;
in vec2 v_texcoord;
layout(location = 0) out vec4 fragColor;

void main()
{
    vec4 source = texture(tex, v_texcoord);
    vec3 c = source.rgb;

    float peak = max(c.r, max(c.g, c.b));
    float shadow = 1.0 - clamp(peak, 0.0, 1.0);
    c *= 1.0 - BLACK_DEPTH * shadow * shadow;

    vec2 p = v_texcoord * 2.0 - 1.0;
    float radius2 = 0.5 * dot(p, p);
    float vignette = smoothstep(VIGNETTE_START, 1.0, radius2);
    c *= 1.0 - VIGNETTE_STRENGTH * vignette;

    fragColor = vec4(clamp(c, 0.0, 1.0), source.a);
}
