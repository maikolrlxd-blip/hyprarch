// hyprarch-wbar — botones de ventana (minimizar, maximizar, cerrar) para la ventana ACTIVA.
//
// C + Wayland + cairo, sin GTK ni Python: unos pocos MB de memoria y 0 % de CPU en reposo. Una sola pastilla pequeña se
// pega sobre la esquina superior derecha de la ventana activa y la sigue. Se despierta con los eventos de Hyprland (socket2);
// solo consulta la geometría con un temporizador cuando la ventana es flotante (arrastrarla no genera eventos).
// Los iconos se dibujan con trazos (nada de tipografías ni fontconfig).
//
//   «–» minimiza (hyprarch-win)   «□» maximiza / restaura   «×» cierra
//
// Archivo ~/.config/hyprarch/wbar:  on = siempre · off = nunca · (ausente) = solo si el equipo no es modesto (perfil lite).
#define _GNU_SOURCE
#include <cairo/cairo.h>
#include <errno.h>
#include <fcntl.h>
#include <math.h>
#include <poll.h>
#include <signal.h>
#include <spawn.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <sys/file.h>
#include <sys/mman.h>
#include <sys/socket.h>
#include <sys/un.h>
#include <unistd.h>
#include <wayland-client.h>

#include "wlr-layer-shell-unstable-v1-client-protocol.h"

extern char **environ;

#define W 108
#define H 26
#define CELL (W / 3)

static struct wl_display *dpy;
static struct wl_compositor *comp;
static struct wl_shm *shm;
static struct zwlr_layer_shell_v1 *lsh;
static struct wl_seat *seat;
static struct wl_pointer *ptr;
static struct wl_surface *surf;
static struct zwlr_layer_surface_v1 *ls;
static struct wl_buffer *buf;
static void *pix;
static int configured;

static int visible, hover = -1, fs, floating_win;
static char addr[32];
static int win_x, win_y, win_w;
static int last_left = -1, last_top = -1;

static char hypr_dir[512];

// ---------- configuración ----------
static int read_small(const char *path, char *out, size_t n) {
    FILE *f = fopen(path, "r");
    if (!f) return 0;
    size_t k = fread(out, 1, n - 1, f);
    fclose(f);
    out[k] = 0;
    while (k && (out[k - 1] == '\n' || out[k - 1] == ' ')) out[--k] = 0;
    return 1;
}

static int wanted(void) {
    char cfg[512], path[640], v[64];
    const char *x = getenv("XDG_CONFIG_HOME"), *h = getenv("HOME");
    if (x && *x) snprintf(cfg, sizeof cfg, "%s/hyprarch", x);
    else snprintf(cfg, sizeof cfg, "%s/.config/hyprarch", h ? h : "");
    snprintf(path, sizeof path, "%s/wbar", cfg);
    if (read_small(path, v, sizeof v)) {
        if (!strcasecmp(v, "on")) return 1;
        if (!strcasecmp(v, "off")) return 0;
    }
    snprintf(path, sizeof path, "%s/perf.effective", cfg);
    if (read_small(path, v, sizeof v)) return strcmp(v, "lite") != 0;
    return 1;
}

// ---------- JSON mínimo (la salida de Hyprland es regular) ----------
static const char *jkey(const char *j, const char *key) {
    char pat[64];
    snprintf(pat, sizeof pat, "\"%s\"", key);
    const char *p = strstr(j, pat);
    if (!p) return NULL;
    p += strlen(pat);
    while (*p == ' ' || *p == '\t' || *p == '\n' || *p == ':') p++;
    return p;
}
static int jint(const char *j, const char *key, int *v) {
    const char *p = jkey(j, key);
    if (!p) return 0;
    if (!strncmp(p, "true", 4)) { *v = 1; return 1; }
    if (!strncmp(p, "false", 5)) { *v = 0; return 1; }
    *v = atoi(p);
    return 1;
}
static int jstr(const char *j, const char *key, char *out, size_t n) {
    const char *p = jkey(j, key);
    if (!p || *p != '"') return 0;
    p++;
    size_t i = 0;
    while (*p && *p != '"' && i + 1 < n) out[i++] = *p++;
    out[i] = 0;
    return 1;
}
static int jpair(const char *j, const char *key, int *a, int *b) {
    const char *p = jkey(j, key);
    if (!p || *p != '[') return 0;
    *a = atoi(p + 1);
    const char *c = strchr(p, ',');
    if (!c) return 0;
    *b = atoi(c + 1);
    return 1;
}

// ---------- Hyprland ----------
static int hypr_connect(const char *name) {
    struct sockaddr_un a = {.sun_family = AF_UNIX};
    snprintf(a.sun_path, sizeof a.sun_path, "%s/%s", hypr_dir, name);
    int fd = socket(AF_UNIX, SOCK_STREAM | SOCK_CLOEXEC, 0);
    if (fd < 0) return -1;
    if (connect(fd, (struct sockaddr *)&a, sizeof a) < 0) { close(fd); return -1; }
    return fd;
}

static int hypr_query(const char *cmd, char *out, size_t n) {
    int fd = hypr_connect(".socket.sock");
    if (fd < 0) return 0;
    struct timeval tv = {1, 0};
    setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof tv);
    if (write(fd, cmd, strlen(cmd)) < 0) { close(fd); return 0; }
    size_t k = 0;
    ssize_t r;
    while (k + 1 < n && (r = read(fd, out + k, n - 1 - k)) > 0) k += (size_t)r;
    close(fd);
    out[k] = 0;
    return k > 0;
}

static void run(char *const argv[]) {
    pid_t pid;
    posix_spawnp(&pid, argv[0], NULL, NULL, argv, environ);
}

static void act(int cell) {
    if (!addr[0]) return;
    if (cell == 0) {
        char *a[] = {"hyprarch-win", "minimize", NULL};
        run(a);
    } else if (cell == 1) {
        char *a[] = {"hyprarch-win", fs == 1 ? "down" : "max", NULL};
        run(a);
    } else {
        char lua[160];
        snprintf(lua, sizeof lua, "hl.dispatch(hl.dsp.window.close({ window = \"address:%s\" }))", addr);
        char *a[] = {"hyprctl", "eval", lua, NULL};
        run(a);
    }
}

// ---------- dibujo ----------
static void rrect(cairo_t *c, double x, double y, double w, double h, double r) {
    cairo_new_sub_path(c);
    cairo_arc(c, x + w - r, y + r, r, -M_PI / 2, 0);
    cairo_arc(c, x + w - r, y + h - r, r, 0, M_PI / 2);
    cairo_arc(c, x + r, y + h - r, r, M_PI / 2, M_PI);
    cairo_arc(c, x + r, y + r, r, M_PI, 3 * M_PI / 2);
    cairo_close_path(c);
}

static void draw(void) {
    cairo_surface_t *cs = cairo_image_surface_create_for_data(pix, CAIRO_FORMAT_ARGB32, W, H, W * 4);
    cairo_t *c = cairo_create(cs);
    cairo_set_operator(c, CAIRO_OPERATOR_CLEAR);
    cairo_paint(c);
    cairo_set_operator(c, CAIRO_OPERATOR_OVER);
    if (visible) {
        rrect(c, 0.5, 0.5, W - 1, H - 1, 12.5);
        cairo_set_source_rgba(c, 0.039, 0.063, 0.094, 0.92);
        cairo_fill_preserve(c);
        cairo_set_source_rgba(c, 1, 1, 1, 0.12);
        cairo_set_line_width(c, 1);
        cairo_stroke(c);
        for (int i = 0; i < 3; i++) {
            double cx = i * CELL + CELL / 2.0, cy = H / 2.0;
            int on = (hover == i);
            if (on) {                                  // fondo del botón al pasar el ratón (rojo para cerrar)
                rrect(c, i * CELL + 2, 3, CELL - 4, H - 6, 10);
                if (i == 2) cairo_set_source_rgba(c, 1.0, 0.353, 0.431, 1);
                else cairo_set_source_rgba(c, 1, 1, 1, 0.16);
                cairo_fill(c);
            }
            cairo_set_source_rgba(c, 1, 1, 1, on ? 1.0 : 0.80);
            cairo_set_line_width(c, 1.4);
            cairo_set_line_cap(c, CAIRO_LINE_CAP_ROUND);
            if (i == 0) {                              // minimizar: raya
                cairo_move_to(c, cx - 4.5, cy + 2);
                cairo_line_to(c, cx + 4.5, cy + 2);
            } else if (i == 1) {                       // maximizar: cuadrado (o dos si ya está maximizada)
                if (fs == 1) {
                    cairo_rectangle(c, cx - 4.5, cy - 2.5, 6, 6);
                    cairo_move_to(c, cx - 2.5, cy - 4.5);
                    cairo_line_to(c, cx + 4.5, cy - 4.5);
                    cairo_line_to(c, cx + 4.5, cy + 2.5);
                } else {
                    cairo_rectangle(c, cx - 4.5, cy - 4.5, 9, 9);
                }
            } else {                                   // cerrar: X
                cairo_move_to(c, cx - 4, cy - 4);
                cairo_line_to(c, cx + 4, cy + 4);
                cairo_move_to(c, cx + 4, cy - 4);
                cairo_line_to(c, cx - 4, cy + 4);
            }
            cairo_stroke(c);
        }
    }
    cairo_destroy(c);
    cairo_surface_destroy(cs);
    // sin ventana que acompañar: sin zona de clic (la superficie transparente no bloquea nada)
    if (visible) wl_surface_set_input_region(surf, NULL);
    else {
        struct wl_region *r = wl_compositor_create_region(comp);
        wl_surface_set_input_region(surf, r);
        wl_region_destroy(r);
    }
    wl_surface_attach(surf, buf, 0, 0);
    wl_surface_damage_buffer(surf, 0, 0, W, H);
    wl_surface_commit(surf);
}

static void place(int left, int top) {
    if (left == last_left && top == last_top) return;
    last_left = left;
    last_top = top;
    zwlr_layer_surface_v1_set_margin(ls, top, 0, 0, left);
    wl_surface_commit(surf);
}

// ---------- ventana activa ----------
static int skip_class(const char *c) {
    static const char *s[] = {"hyprarch-ai-float", "hyprarch-ai-full", "hyprarch-ai-answer", "local.hyprarch.claudepresence", NULL};
    for (int i = 0; s[i]; i++) if (!strcmp(c, s[i])) return 1;
    return 0;
}

static void refresh(void) {
    static char j[8192];
    int want = 0, mapped = 1, hidden = 0, x = 0, y = 0, w = 0, h = 0, fsv = 0, fl = 0;
    char cls[128] = "", ws[128] = "";
    if (hypr_query("j/activewindow", j, sizeof j) && jstr(j, "address", addr, sizeof addr)) {
        jint(j, "mapped", &mapped);
        jint(j, "hidden", &hidden);
        jint(j, "fullscreen", &fsv);
        jint(j, "floating", &fl);
        jpair(j, "at", &x, &y);
        jpair(j, "size", &w, &h);
        jstr(j, "class", cls, sizeof cls);
        const char *wp = jkey(j, "workspace");
        if (wp) jstr(wp, "name", ws, sizeof ws);
        want = mapped && !hidden && fsv != 2 && strncmp(ws, "special", 7) != 0 && !skip_class(cls);
    } else {
        addr[0] = 0;
    }
    if (!want) {
        if (visible) { visible = 0; draw(); }
        addr[0] = want ? addr[0] : 0;
        return;
    }
    floating_win = fl;
    win_x = x; win_y = y; win_w = w;
    int left = x + w - W - 10, top = y - H - 2;
    if (left < 0) left = 0;
    if (top < 2) top = 2;
    place(left, top);
    if (!visible || fsv != fs) { fs = fsv; visible = 1; draw(); }
}

// ---------- puntero ----------
static void p_enter(void *d, struct wl_pointer *p, uint32_t s, struct wl_surface *sf, wl_fixed_t x, wl_fixed_t y) {
    (void)d; (void)p; (void)s; (void)sf; (void)y;
    hover = wl_fixed_to_int(x) / CELL;
    draw();
}
static void p_leave(void *d, struct wl_pointer *p, uint32_t s, struct wl_surface *sf) {
    (void)d; (void)p; (void)s; (void)sf;
    hover = -1;
    draw();
}
static void p_motion(void *d, struct wl_pointer *p, uint32_t t, wl_fixed_t x, wl_fixed_t y) {
    (void)d; (void)p; (void)t; (void)y;
    int c = wl_fixed_to_int(x) / CELL;
    if (c != hover) { hover = c; draw(); }
}
static void p_button(void *d, struct wl_pointer *p, uint32_t s, uint32_t t, uint32_t b, uint32_t st) {
    (void)d; (void)p; (void)s; (void)t;
    if (b == 0x110 && st == WL_POINTER_BUTTON_STATE_RELEASED && hover >= 0 && hover < 3) act(hover);
}
static void p_axis(void *d, struct wl_pointer *p, uint32_t t, uint32_t a, wl_fixed_t v) { (void)d; (void)p; (void)t; (void)a; (void)v; }
static void p_frame(void *d, struct wl_pointer *p) { (void)d; (void)p; }
static void p_axis_source(void *d, struct wl_pointer *p, uint32_t s) { (void)d; (void)p; (void)s; }
static void p_axis_stop(void *d, struct wl_pointer *p, uint32_t t, uint32_t a) { (void)d; (void)p; (void)t; (void)a; }
static void p_axis_discrete(void *d, struct wl_pointer *p, uint32_t a, int32_t n) { (void)d; (void)p; (void)a; (void)n; }
static const struct wl_pointer_listener ptr_l = {p_enter, p_leave, p_motion, p_button, p_axis, p_frame, p_axis_source, p_axis_stop, p_axis_discrete};

static void seat_caps(void *d, struct wl_seat *s, uint32_t caps) {
    (void)d;
    if ((caps & WL_SEAT_CAPABILITY_POINTER) && !ptr) {
        ptr = wl_seat_get_pointer(s);
        wl_pointer_add_listener(ptr, &ptr_l, NULL);
    }
}
static void seat_name(void *d, struct wl_seat *s, const char *n) { (void)d; (void)s; (void)n; }
static const struct wl_seat_listener seat_l = {seat_caps, seat_name};

// ---------- Wayland ----------
static void reg_global(void *d, struct wl_registry *r, uint32_t name, const char *iface, uint32_t ver) {
    (void)d;
    if (!strcmp(iface, wl_compositor_interface.name)) comp = wl_registry_bind(r, name, &wl_compositor_interface, 4);
    else if (!strcmp(iface, wl_shm_interface.name)) shm = wl_registry_bind(r, name, &wl_shm_interface, 1);
    else if (!strcmp(iface, zwlr_layer_shell_v1_interface.name)) lsh = wl_registry_bind(r, name, &zwlr_layer_shell_v1_interface, ver < 4 ? ver : 4);
    else if (!strcmp(iface, wl_seat_interface.name)) {
        seat = wl_registry_bind(r, name, &wl_seat_interface, ver < 5 ? ver : 5);
        wl_seat_add_listener(seat, &seat_l, NULL);
    }
}
static void reg_remove(void *d, struct wl_registry *r, uint32_t n) { (void)d; (void)r; (void)n; }
static const struct wl_registry_listener reg_l = {reg_global, reg_remove};

static void ls_configure(void *d, struct zwlr_layer_surface_v1 *s, uint32_t serial, uint32_t w, uint32_t h) {
    (void)d; (void)w; (void)h;
    zwlr_layer_surface_v1_ack_configure(s, serial);
    configured = 1;
}
static void ls_closed(void *d, struct zwlr_layer_surface_v1 *s) { (void)d; (void)s; exit(0); }
static const struct zwlr_layer_surface_v1_listener ls_l = {ls_configure, ls_closed};

int main(void) {
    if (!wanted()) return 0;                       // equipo modesto o desactivado: no se carga nada

    const char *rt = getenv("XDG_RUNTIME_DIR"), *sig = getenv("HYPRLAND_INSTANCE_SIGNATURE");
    if (!rt || !sig) return 1;
    snprintf(hypr_dir, sizeof hypr_dir, "%s/hypr/%s", rt, sig);

    char lockp[600];                               // una sola instancia
    snprintf(lockp, sizeof lockp, "%s/hyprarch-wbar.lock", rt);
    int lk = open(lockp, O_CREAT | O_RDWR | O_CLOEXEC, 0600);
    if (lk < 0 || flock(lk, LOCK_EX | LOCK_NB) < 0) return 0;
    signal(SIGCHLD, SIG_IGN);

    dpy = wl_display_connect(NULL);
    if (!dpy) return 1;
    struct wl_registry *reg = wl_display_get_registry(dpy);
    wl_registry_add_listener(reg, &reg_l, NULL);
    wl_display_roundtrip(dpy);
    if (!comp || !shm || !lsh) { fprintf(stderr, "hyprarch-wbar: falta wl_compositor, wl_shm o layer-shell\n"); return 1; }
    wl_display_roundtrip(dpy);

    int fd = memfd_create("wbar", MFD_CLOEXEC);
    if (fd < 0 || ftruncate(fd, W * H * 4) < 0) return 1;
    pix = mmap(NULL, W * H * 4, PROT_READ | PROT_WRITE, MAP_SHARED, fd, 0);
    struct wl_shm_pool *pool = wl_shm_create_pool(shm, fd, W * H * 4);
    buf = wl_shm_pool_create_buffer(pool, 0, W, H, W * 4, WL_SHM_FORMAT_ARGB8888);
    wl_shm_pool_destroy(pool);
    close(fd);

    surf = wl_compositor_create_surface(comp);
    ls = zwlr_layer_shell_v1_get_layer_surface(lsh, surf, NULL, ZWLR_LAYER_SHELL_V1_LAYER_TOP, "hyprarch-wbar");
    zwlr_layer_surface_v1_add_listener(ls, &ls_l, NULL);
    zwlr_layer_surface_v1_set_size(ls, W, H);
    zwlr_layer_surface_v1_set_anchor(ls, ZWLR_LAYER_SURFACE_V1_ANCHOR_TOP | ZWLR_LAYER_SURFACE_V1_ANCHOR_LEFT);
    zwlr_layer_surface_v1_set_exclusive_zone(ls, -1);
    zwlr_layer_surface_v1_set_keyboard_interactivity(ls, ZWLR_LAYER_SURFACE_V1_KEYBOARD_INTERACTIVITY_NONE);
    wl_surface_commit(surf);
    while (!configured) if (wl_display_dispatch(dpy) < 0) return 1;
    draw();                                        // empieza transparente y sin zona de clic

    int ev = hypr_connect(".socket2.sock");
    refresh();
    for (;;) {
        while (wl_display_prepare_read(dpy) != 0) wl_display_dispatch_pending(dpy);
        wl_display_flush(dpy);
        struct pollfd pf[2] = {{wl_display_get_fd(dpy), POLLIN, 0}, {ev, POLLIN, 0}};
        // flotante: se mira su sitio a menudo (arrastrarla no avisa); en mosaico, de vez en cuando; sin ventana: solo eventos
        int timeout = visible ? (floating_win ? 600 : 2800) : 5000;
        int r = poll(pf, ev >= 0 ? 2 : 1, timeout);
        if (r < 0 && errno != EINTR) break;
        if (pf[0].revents & POLLIN) wl_display_read_events(dpy);
        else wl_display_cancel_read(dpy);
        if (wl_display_dispatch_pending(dpy) < 0) break;
        int changed = (r == 0);                    // vencido el plazo: se refresca
        if (ev >= 0 && (pf[1].revents & (POLLIN | POLLHUP))) {
            char junk[4096];
            ssize_t k = read(ev, junk, sizeof junk);
            if (k <= 0) { close(ev); ev = -1; }
            else { changed = 1; usleep(30000); }   // varios eventos seguidos = un solo refresco
        }
        if (changed) refresh();
    }
    return 0;
}
