# Armas y manos visibles (requisito de Maikol para la primera versión)
Estado: el código está escrito y subido, **sin probar en Studio** y **sin las plantillas** (hay que importarlas). Con plantillas ausentes el juego sigue funcionando como ahora (se dispara sin ver el arma).

## Primera persona (viewmodel) — `client/Viewmodel.client.lua`
Plantillas en `ReplicatedStorage > LUTO_VM`: un Model por arma llamado exactamente `pistola`, `escopeta`, `subfusil` (los `*_VM.fbx` de `apocalipsis-arte/armas/<arma>/`: brazos + arma con su rig/huesos). Reglas: el origen del modelo es la cámara (`viewmodel_origen_arma_desde_camara` de `datos.json`), partes sin colisión; los brazos se pintan en cliente con los colores base de `src/Apariencia.lua` (mangas oliva, manos piel); un `Animator`/`AnimationController` dentro del modelo. El script lo pega a la cámara solo en primera persona, oculta el cuerpo del personaje y reproduce los clips al recibir `LUTO_Anim` (Equipar, Disparo, Bombear, Recargar, Recargar_Inicio/_Cartucho/_Fin, Inspeccionar; Reposo en bucle).
## Tercera persona (arma en la mano) — `server/Armas.server.lua`
Plantillas en `ReplicatedStorage > LUTO_Armas`: un `Tool` por arma (`pistola`, `escopeta`, `subfusil`) con `Handle` (MeshPart del `*_Mundo.fbx` ya con textura) y `Grip` ajustado para que el arma quede bien en la mano derecha del R15 (`Pistola9mm_Eventos.lua` da `HandleCentroDesdeOrigen` y los puntos Boca/Expulsion). El servidor lo equipa al cambiar de arma (1/2/3) y al reaparecer.
## Animaciones
`src/Animaciones.lua`: ids de cada clip por arma (`pistola`, `escopeta`, `subfusil`): clips del viewmodel (los `*_VM_*.fbx` de `clips/`). Publicar con el Animation Editor como se hizo con la zombi (cuenta de Maikol) y rellenar los ids.
## Qué probar en Studio
Entrar en Play: se ve el arma y los brazos (manga oliva, mano piel) abajo a la derecha; disparar mueve el arma (Disparo); R recarga (Recargar); F inspecciona; 1/2/3 cambian de arma (Equipar); en tercera persona se ve el arma en la mano; sin brazos del avatar de Roblox tapando.
