# Contrato servidor ↔ interfaz (borrador de Claude nube, 30/10) — SIN PROBAR EN STUDIO
Propuesta para que el servidor (Coordinador) y la UI (Claude nube) se entiendan. Cámbialo con un commit si hace falta.

## Atributos del jugador (el servidor los escribe; la UI solo lee)
Energia, EnergiaMax, Potencia, Puntos, Distancia, ZonaMult, Aros, ArosTotal, Mascota, MascotaBonus, Rebirths, Alas (id equipadas), EnVuelo (bool), Planeando (bool).

## RemoteEvents (ReplicatedStorage)
- `MAS1_Accion` (cliente→servidor): `"boost" (bool)`, `"ataque"`, `"lateral" (-1|0|1)`, `"lanzar"`, `"equipar", tipo, id`, `"abrirHuevo", rareza`, `"rebirth"`, `"comprarAla", id`. El servidor valida todo.
- `MAS1_Efecto` (servidor→clientes): nombre de efecto de `src/Efectos.lua` + posición.
- `MAS1_Resultado` (servidor→cliente): `{ distancia, aros, golpes, multiplicador, dinero, exp }` al aterrizar (forma de `Vuelo.aterrizar`).
- `MAS1_Huevo` (servidor→cliente): `{ rareza, mascotaId }` al abrir un huevo.
- `MAS1_Inventario` (servidor→cliente): `{ mascotas = {id=cantidad}, equipadas = {ids}, alas = {ids} }`.

## Datos
`src/Mascotas.lua` (ids, rarezas, bonus), `src/Vuelo.lua` (reglas). La UI no calcula bonus: los pide al servidor.
