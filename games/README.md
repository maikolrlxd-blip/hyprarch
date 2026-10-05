# Juegos para Play Store

Tres juegos HTML5 (canvas, sin dependencias ni assets externos, funcionan offline) empaquetados como apps Android con un WebView.

| Juego | Estilo | Cómo se juega |
|---|---|---|
| `stack-tower` | 3D isométrico | Toca para soltar el bloque; lo que sobresale se corta. Los "perfectos" encadenan racha y recuperan tamaño. |
| `gravity-flip` | Runner 2D infinito | Toca para invertir la gravedad (suelo/techo). Esquiva pinchos y bloques, recoge orbes. |
| `space-blaster` | Shooter arcade 2D | Arrastra para mover la nave (dispara sola). Oleadas, 4 power-ups, jefe cada 5 oleadas. |

Todos guardan el récord en `localStorage`, usan sonido WebAudio generado por código y se adaptan a cualquier tamaño de pantalla. Se pueden probar en el navegador abriendo `<juego>/index.html`.

## Generar la app Android

```bash
./build-android.sh stack-tower          # genera build/stack-tower-android/ (abrir en Android Studio)
./build-android.sh stack-tower --apk    # además compila el APK debug (requiere Android SDK y gradle)
```

Cada juego recibe su propio `applicationId` (`com.hyprarch.games.<juego>`). El proyecto usa AGP 8.9.1, compileSdk/targetSdk 36, minSdk 24 y no pide permisos.

## Antes de publicar en Play Store

- Crear un keystore y generar un **AAB firmado** (`Build > Generate Signed Bundle`); Play exige AAB.
- Sustituir el icono por defecto (`res/drawable/ic_fg.xml`) y preparar capturas, icono 512x512 y gráfico de funciones.
- Declarar en la ficha la política de privacidad y el cuestionario de clasificación (los juegos no recopilan datos).
- Ajustar `versionCode`/`versionName` en `app/build.gradle` en cada subida.
