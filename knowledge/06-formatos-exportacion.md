# 06 — Formatos de Exportación para Redes Sociales

## Matriz de formatos por plataforma y tipo de contenido

| Plataforma | Tipo | Formato | Calidad | Notas |
|---|---|---|---|---|
| Instagram feed foto | Imagen | JPEG | 80–85% | sRGB obligatorio |
| Instagram feed gráfico | Imagen | PNG-24 | — | Sin compresión visible |
| Instagram Stories foto | Imagen | JPEG | 85% | |
| Instagram Stories gráfico | Imagen | PNG-24 | — | |
| Instagram Reels | Video | MP4 H.264 | alta | Ver specs abajo |
| TikTok | Video | MP4 H.264 | alta | |
| LinkedIn foto | Imagen | JPEG | 85% | |
| LinkedIn carrusel | PDF | PDF/X-1a o PDF estándar | — | Imágenes a 72dpi embedded |
| Pinterest | Imagen | JPEG o PNG | 85% / sin pérdida | PNG para gráficos con texto |
| YouTube thumbnail | Imagen | JPEG | 90% | Máx 2MB |
| Facebook | Imagen | JPEG | 80% | |

---

## JPEG vs PNG — Cuándo usar cada uno

### Usar JPEG cuando:
- La imagen es una foto o tiene gradientes complejos
- El fondo no es transparente
- Se prioriza el peso del archivo
- No hay texto pequeño ni bordes definidos

### Usar PNG cuando:
- Hay texto en la imagen (bordes nítidos, sin artefactos)
- El fondo es sólido o transparente
- Hay ilustraciones con áreas de color plano
- La imagen va a ser reusada o editada después
- Gráficos con líneas finas o detalles pequeños

### La "paradoja del PNG en Instagram"
Instagram recomprime todo al subir. Sin embargo:
- PNG garantiza que la imagen sube con mayor calidad inicial antes de la recompresión
- Para gráficos con texto: PNG > JPEG (los artefactos JPEG ensucian los bordes del texto)
- Para fotos: JPEG 85–90% es suficiente

---

## Exportación desde Photoshop

### Export As (método recomendado)
```
File > Export > Export As (Shift+Alt+Cmd/Ctrl+W)

Para JPEG:
  Format: JPEG
  Quality: 80–85 (no más, Instagram recomprime igual)
  Resize: solo si necesitás reducir (nunca subir)
  Color Space: Convert to sRGB ✓
  Embed Color Profile ✓

Para PNG:
  Format: PNG
  Interlaced: OFF
  Color Space: Convert to sRGB ✓
```

### Save for Web (método legacy, aún válido)
```
File > Export > Save for Web (Alt+Shift+Cmd/Ctrl+S)

Activar "4-Up" para comparar calidades
Verificar peso final en el preview
Ideal para optimizar el balance calidad/peso visualmente
```

### Batch Export con Actions
```
File > Automate > Batch
Set: el set que contiene tu Action de exportación
Source: carpeta de archivos .psd
Destination: carpeta de salida
Override Action "Save As" commands: ✓
```

---

## Exportación desde Illustrator

### Export for Screens (método principal)
```
File > Export > Export for Screens (Shift+Cmd/Ctrl+E)

Artboards: seleccionar los que exportar
Add scale: 1× para tamaño final
Format: JPEG (fotos) o PNG (gráficos)
Suffix: opcional, agregar nombre de red social

Para múltiples resoluciones simultáneas:
  Add scale > 1× (normal) + 2× (retina)
  Los nombres se generan automáticamente: archivo@2x
```

### Export Assets
```
Window > Asset Export
Seleccionar elementos del canvas
Añadir a Asset Export panel
Exportar todos con un clic
Ideal para iconos e ilustraciones reutilizables
```

---

## Especificaciones de video para social media

### Instagram Reels / TikTok / YouTube Shorts
```
Códec de video: H.264 (MP4)
Códec de audio: AAC, 128 kbps o superior
Resolución: 1080×1920 px
Frame rate: 24fps (cinematográfico), 30fps (estándar), 60fps (fluido)
Bitrate de video: 8–15 Mbps (no impacta en subida, plataformas recomprimen)
Duración: 
  Reels: 3 seg a 15 min (15–60 seg óptimo para alcance)
  TikTok: hasta 10 min (7–30 seg óptimo para retención)
  Shorts: hasta 60 seg
Peso máximo: 4GB (Reels), 287.6MB (TikTok para móvil), 256GB (YouTube)
```

### YouTube Videos
```
Resolución: 3840×2160 (4K), 1920×1080 (HD), mínimo 1280×720
Frame rate: mismo que el footage original
Códec: H.264 o H.265 para uploads más rápidos
Formato contenedor: MP4, MOV, AVI
Bitrate recomendado para subida (YouTube recomprime):
  1080p 30fps: 8 Mbps
  1080p 60fps: 12 Mbps
  4K 30fps: 35–45 Mbps
```

### Facebook Video
```
Resolución: 1080×1080 (cuadrado), 1080×1920 (vertical), 1920×1080 (horizontal)
Códec: H.264
Frame rate: 30fps
Duración máxima: 240 minutos
Peso máximo: 10GB
```

---

## Optimización de peso para carga rápida

### Herramientas de compresión adicionales (post-exportación)
```
TinyPNG / TinyJPG:  comprimir PNG y JPEG manteniendo calidad visual
Squoosh (Google):   control avanzado, múltiples formatos incluyendo WebP
ImageOptim (Mac):   compresión sin pérdida, ideal para lotes
```

### Objetivos de peso por formato
```
Instagram feed (JPEG):     < 1 MB (idealmente 300–600 KB)
Instagram Stories (PNG):   < 2 MB
Stories animados/video:    < 4 GB (pero comprimir al máximo razonable)
Pinterest (JPEG):          < 500 KB
YouTube thumbnail (JPEG):  < 2 MB (límite de la plataforma)
LinkedIn (JPEG):           < 5 MB
```

---

## Color management en exportación

### Verificar perfil de color embebido
```
Photoshop: Edit > Assign Profile (verificar, no cambiar) → debe decir sRGB
Illustrator: File > Document Color Mode → debe decir RGB Color
Al exportar: siempre marcar "Convert to sRGB" y "Embed Color Profile"
```

### El problema del Perceptual vs Relative Colorimetric
```
Al convertir perfiles de color:
  Perceptual: mejor para fotos (preserva la relación entre colores)
  Relative Colorimetric: mejor para gráficos con colores específicos de marca
  
En social media: usar Perceptual para todo (las plataformas lo manejan mejor)
```

---

## Checklist de exportación antes de publicar

```
□ Dimensiones exactas verificadas (no "aproximadas")
□ Modo de color: RGB (no CMYK)
□ Perfil: sRGB embebido
□ Texto legible al 100% de zoom
□ Logo visible en la versión pequeña (feed preview)
□ Zona segura respetada (Stories/Reels)
□ Peso dentro del límite de la plataforma
□ Nombre de archivo limpio (sin caracteres especiales, sin espacios)
□ Preview en dispositivo móvil antes de publicar
□ Versión para historia y versión para feed exportadas por separado (si aplica)
```
