# Juegos para Play Store

## ⭐ Void Survivors (juego principal)

Roguelite de supervivencia espacial con progresión permanente, hecho en HTML5/Canvas y empaquetado como app Android (WebView).
Es el juego "de verdad": ver [`void-survivors/README.md`](void-survivors/README.md) para sistemas, estructura y herramientas de balance.

- Partidas de ~7-8 min, control con un dedo, hordas, élites, 3 jefes, 6 armas con **evoluciones**, 10 pasivos, 3 fases.
- Meta: 11 mejoras permanentes, 5 naves, misiones diarias, racha de login, 17 logros, español/inglés.
- Calidad: simulación separada del render y probada con bots (equilibrio) y 17 pruebas automáticas (`node void-survivors/tools/test.js`).
- Listo para tienda: textos, política de privacidad, icono, gráfico de funciones y capturas en `void-survivors/store/`.

## Prototipos pequeños

`stack-tower`, `gravity-flip` y `space-blaster` son prototipos de una sola pantalla (un fichero HTML cada uno). Sirven de base, pero por sí solos tienen poco gancho de retención.

## Generar la app Android

```bash
./build-android.sh void-survivors          # genera build/void-survivors-android/ (abrir en Android Studio)
./build-android.sh void-survivors --apk    # además compila el APK debug (requiere Android SDK y gradle 8.11+)
```

Sin instalar nada: el workflow **Build Android games** (`.github/workflows/android-games.yml`, botón *Run workflow*) compila el APK debug y el AAB release en GitHub y los deja como artefactos. Si añades los secretos `KEYSTORE_BASE64`, `KEYSTORE_PASSWORD`, `KEY_ALIAS` y `KEY_PASSWORD`, el AAB sale firmado.

Cada juego recibe su `applicationId` (`com.hyprarch.games.<juego>`). El proyecto usa AGP 8.9.1, compileSdk/targetSdk 36 y minSdk 24; el único permiso es VIBRATE.

> Nota: el proyecto Android no se ha podido compilar en el entorno donde se escribió (sin SDK). Los juegos sí se probaron en Chromium; si Gradle se queja de alguna versión, ajusta `android-template/build.gradle` y `app/build.gradle`.

## Pasos para publicar en Play Store

Ver [`void-survivors/store/README.md`](void-survivors/store/README.md).
