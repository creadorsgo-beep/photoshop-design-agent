# 01 — Especificaciones Técnicas por Plataforma

## Instagram

### Feed
| Formato | Dimensiones | Relación | Resolución | Peso máx |
|---|---|---|---|---|
| Cuadrado | 1080×1080 px | 1:1 | 72 dpi | 30 MB |
| Vertical | 1080×1350 px | 4:5 | 72 dpi | 30 MB |
| Horizontal | 1080×566 px | 1.91:1 | 72 dpi | 30 MB |

**Zona segura feed vertical (4:5):** contenido crítico entre y=135 y y=1215 (evitar 135px superiores e inferiores que la UI puede recortar en algunos dispositivos).

### Stories / Reels
| Formato | Dimensiones | Zona segura superior | Zona segura inferior |
|---|---|---|---|
| Stories | 1080×1920 px | 250 px | 250 px |
| Reels | 1080×1920 px | 250 px | 400 px (controles de UI) |

**Zona segura lateral Stories:** 60 px a cada lado.
**Stickers interactivos:** se ubican entre y=630 y y=1490.

### Carrusel
- Mismas dimensiones que feed
- Consistencia visual entre slides: mantener elementos anclados (logo, fondo) en la misma posición
- Primera imagen debe funcionar como standalone (es la que aparece en el perfil)

---

## Facebook

| Formato | Dimensiones | Notas |
|---|---|---|
| Post imagen | 1200×630 px | Relación 1.91:1 óptima |
| Post cuadrado | 1080×1080 px | Funciona en feed y compartido |
| Cover page | 820×312 px (desktop) / 640×360 px (mobile) | Diseñar a 820×312, zona segura 560×180 px centrada |
| Event cover | 1920×1005 px | |
| Stories | 1080×1920 px | Igual que Instagram |
| Anuncio link | 1200×628 px | |

**Texto en anuncios:** Facebook penaliza imágenes con más del 20% de superficie cubierta por texto.

---

## TikTok

| Formato | Dimensiones | FPS recomendado | Duración |
|---|---|---|---|
| Video vertical | 1080×1920 px | 24–60 fps | hasta 10 min |
| Cover/thumbnail | 1080×1920 px | — | — |

**Zona segura TikTok:**
- Superior: 130 px (barra de estado + logo)
- Inferior: 380 px (controles, descripción, música)
- Derecha: 130 px (botones de interacción)
- Izquierda: libre

**Texto en pantalla:** nunca debajo de y=1540 (quedará tapado por UI).

---

## LinkedIn

| Formato | Dimensiones | Notas |
|---|---|---|
| Post imagen | 1200×627 px | Relación 1.91:1 |
| Post cuadrado | 1080×1080 px | |
| Documento (carrusel PDF) | 1080×1080 px o 1920×1080 px | Máximo 300 páginas, 100 MB |
| Cover banner personal | 1584×396 px | |
| Cover banner empresa | 1128×191 px | |
| Stories | 1080×1920 px | |

---

## Pinterest

| Formato | Dimensiones | Relación | Notas |
|---|---|---|---|
| Pin estándar | 1000×1500 px | 2:3 | Óptimo para feed |
| Pin cuadrado | 1000×1000 px | 1:1 | |
| Pin largo | 1000×2100 px | 1:2.1 | Máximo recomendado |
| Video Pin | 1000×1500 px | 2:3 | |

**Zona segura:** 60 px en todos los bordes. Texto descriptivo en el tercio inferior.

---

## YouTube

| Formato | Dimensiones | Notas |
|---|---|---|
| Thumbnail | 1280×720 px | 72 dpi, máx 2 MB, JPG/PNG/GIF/WebP |
| Banner | 2560×1440 px | Zona segura: 1546×423 px centrada |
| Shorts thumbnail | 1080×1920 px | |
| End card | área 1280×720, elementos mínimo 98×55 px | |

**Thumbnail best practices:**
- Texto máximo 6 palabras, tamaño mínimo 60px a 1280px de ancho
- Contraste alto: el thumbnail se ve en tamaños desde 168×94 px hasta full HD
- Zona segura: evitar los 20 px del borde derecho (botón de agregar a lista)

---

## X (Twitter)

| Formato | Dimensiones | Notas |
|---|---|---|
| Tweet imagen | 1600×900 px | Relación 16:9 para vista completa |
| Tweet cuadrado | 1080×1080 px | |
| Header | 1500×500 px | Zona segura: 1260×360 px centrada |

---

## WhatsApp Status

| Formato | Dimensiones | Duración |
|---|---|---|
| Imagen | 1080×1920 px | 24h |
| Video | 1080×1920 px | máx 30 seg |

---

## Configuración de archivo en Adobe

### Photoshop — Configuración recomendada para redes sociales
```
Modo de color: RGB
Profundidad: 8 bits (suficiente para JPEG/PNG web)
Espacio de color: sRGB IEC61966-2.1
Resolución: 72 ppi (los píxeles son lo que importa, no los dpi)
Compresión PNG: ninguna para edición, máxima para exportación web
```

### Illustrator — Configuración documento
```
Modo de color: RGB
Unidades: Píxeles
Perfil de color: sRGB IEC61966-2.1
Rasterizar efectos (Document Raster Effects Settings): 72 ppi (Screen)
Alineación de píxeles: activada (Pixel Preview para verificar)
```

### Regla de resolución para exportación
- Feed/Stories: 1× (exportar al tamaño del documento)
- Si el documento está a 2× (2160×2160): exportar al 50%
- Nunca subir de resolución: si el documento es pequeño, rediseñar
