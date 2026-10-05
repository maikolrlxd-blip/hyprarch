# Publicar Void Survivors en Google Play

Material ya preparado en esta carpeta:

| Archivo | Para qué |
|---|---|
| `LISTING.md` | Título, descripciones corta/larga (ES/EN), categoría, etiquetas |
| `PRIVACY.md` | Política de privacidad (hay que alojarla en una URL pública y poner tu correo) |
| `graphics/icon-512.png` | Icono de la ficha (512×512) |
| `graphics/feature-1024x500.png` | Gráfico de funciones (1024×500) |
| `graphics/phone-*.png` | 8 capturas de teléfono (1080×1920) |
| `video/clip-*.mp4` | 3 clips verticales de gameplay real (sin audio) para Shorts/TikTok/Reels/Reddit |
| `GROWTH.md` | Investigación de mercado, qué se aplicó y plan de lanzamiento por fases |

Regenerar: `node ../tools/store-assets.js` (gráficos) y `node ../tools/make-clips.js` (vídeos; requiere ffmpeg).

## Checklist (lo que solo puedes hacer tú)

1. **Cuenta de desarrollador de Google Play** (pago único de 25 USD) y verificación de identidad.
2. **Compilar el AAB firmado**: lanza el workflow *Build Android games* en GitHub con los 4 secretos de firma (crea el keystore con `keytool -genkeypair -v -keystore release.jks -alias upload -keyalg RSA -keysize 2048 -validity 10000`, y guarda `base64 -w0 release.jks` en `KEYSTORE_BASE64`). **Guarda el keystore**: sin él no puedes actualizar la app.
3. **Política de privacidad**: publica `PRIVACY.md` en una URL (p. ej. GitHub Pages), sustituye tu correo y pon esa URL en la ficha y en `PRIVACY_URL` de `js/main.js`.
4. **Ficha de la tienda**: copia los textos de `LISTING.md` y sube los gráficos.
5. **Cuestionarios de la consola**: clasificación de contenido (violencia de fantasía leve), seguridad de los datos ("no se recopilan datos"), público objetivo, anuncios (esta versión: no contiene anuncios).
6. **Prueba cerrada**: las cuentas personales nuevas deben tener un mínimo de testers (actualmente 12) durante 14 días antes de pasar a producción.
7. **Subir el AAB** a pruebas internas primero y probar en un móvil real (rendimiento, audio, botón Atrás, pantallas con muesca).

## Ideas para después del lanzamiento

- Anuncios recompensados (AdMob): el juego ya llama a `window.AndroidAds`; falta implementar `MainActivity.AdsBridge` con el SDK. Al activarlos, actualiza la política de privacidad y el cuestionario de datos.
- Marcadores/Play Games, copias de seguridad en la nube, más fases/jefes/naves (todo está en `js/data.js`).
