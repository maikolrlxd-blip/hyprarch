# Seguridad

hyprarch da a una IA acceso controlado al escritorio, así que la seguridad importa.

## Cómo reportar una vulnerabilidad
**No abras una *issue* pública.** Usa *Security → Report a vulnerability* de este repositorio (aviso privado de GitHub).
Incluye: qué pasa, cómo reproducirlo y qué impacto tiene. Responderé lo antes posible.

## Qué se considera importante
- Que una IA ejecute algo **sin que la persona pulse «Permitir»** (saltarse la tarjeta de permisos o `hyprarch-api`).
- Que el informe de problemas envíe datos que no debería (usuario, equipo, MAC, IP, contraseñas, redes Wi-Fi).
- Que la ISO pública incluya credenciales, llaves o software propietario de una IA.
- Fallos del instalador que borren un disco distinto del elegido.

## Qué NO hace hyprarch
Sin telemetría. No guarda contraseñas ni llaves de las IAs. No abre el equipo a internet por su cuenta.
