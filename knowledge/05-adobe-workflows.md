# 05 — Workflows en Adobe para Redes Sociales

## Photoshop — Workflows de producción

### Estructura de capas para piezas sociales

```
📁 [NOMBRE_PIEZA] — 1080x1080 — Instagram Feed
  📁 UI / Marca
    🖼 Logo
    📝 Handle (@marca)
  📁 Texto
    📝 CTA
    📝 Subtítulo  
    📝 Titular
  📁 Elementos gráficos
    ⬜ Formas / Fondos de texto
    ✨ Efectos decorativos
  📁 Producto / Sujeto
    🖼 Sujeto (con máscara)
    💡 Luz de relleno (capa de ajuste con Clipping Mask)
    🌑 Sombra de sujeto
  📁 Corrección de color
    🎨 Color Lookup (LUT de marca)
    🎨 Vibrance
    🎨 Curves (luminosidad general)
  📁 Fondo
    ⬜ Textura / Patrón
    🎨 Color de fondo
```

### Smart Objects — reglas de uso obligatorio

**Siempre convertir a Smart Object:**
- Logos (nunca rasterizar)
- Fotos de producto (para edición no destructiva)
- Elementos que se repiten en múltiples formatos

**Beneficios en producción social:**
- Editar el SO actualiza todas las instancias (vinculadas)
- Aplicar filtros inteligentes (reversibles)
- Escalar sin pérdida de calidad

**Linked Smart Objects para sistemas de contenido:**
```
File > Place Linked (en vez de Embed)
El archivo SO vive en disco
Cambiar el archivo fuente actualiza todas las piezas que lo usan
Ideal para: logo, fondos de marca, plantillas de foto
```

### Actions para producción en serie

**Action de exportación multi-formato:**
```
Action: "Exportar redes sociales"
Pasos grabados:
1. File > Export > Export As
   Format: JPEG, Quality: 80–85
   sRGB: checked
   Guardar en carpeta /exports/instagram-feed/
2. Image > Image Size > 1080×1920 (Stories)
3. Export As > guardar en /exports/stories/
4. Undo Image Size (volver al original)
```

**Action de preparación de foto:**
```
Action: "Prep foto social"
1. Convert to Smart Object
2. Filter > Camera Raw Filter
3. Layer > New Adjustment Layer > Curves (ajuste base de marca)
4. Layer > New Adjustment Layer > Vibrance (+15)
5. Layer > New Adjustment Layer > Color Lookup > LUT de marca
```

### Photoshop — Atajos de productividad

```
Cmd/Ctrl + J          Duplicar capa
Cmd/Ctrl + G          Agrupar capas seleccionadas
Cmd/Ctrl + Alt + G    Crear Clipping Mask
Cmd/Ctrl + T          Transformación libre
Cmd/Ctrl + Shift + E  Merge visible (ojo: destructivo)
Alt + clic en ojo     Aislar capa visualmente
Cmd/Ctrl + clic en miniatura   Seleccionar píxeles de la capa
V + clic sobre objeto Seleccionar capa por clic directo en canvas
```

---

## Illustrator — Workflows para social media

### Artboards para producción multi-formato

**Configurar múltiples artboards desde el inicio:**
```
New Document > More Settings
Añadir artboards para cada formato:
- 1080×1080 (Feed cuadrado)
- 1080×1350 (Feed 4:5)
- 1080×1920 (Stories)
- 1200×628 (Facebook)
- 1280×720 (YouTube thumbnail)

Window > Artboards (para gestionar nombres y orden)
```

**Exportar artboards individualmente:**
```
File > Export > Export for Screens
Seleccionar artboards específicos
Formato: PNG/JPEG/SVG
Escala: 1× (si el documento ya está a la resolución final)
```

### Símbolos en Illustrator

**Para elementos repetidos (logo, iconos, elementos de marca):**
```
Seleccionar objeto > Window > Symbols > menú > New Symbol
Beneficio: editar el símbolo actualiza todas las instancias
Diferencia con Ps: los símbolos de Ai son vectoriales, escalan perfecto
```

### Variables en Illustrator (Data-Driven Graphics)

**Para producir piezas en serie con datos diferentes:**
```
Window > Variables
Definir variables: texto y/o imagen
Vincular objetos del canvas a variables
File > Scripts > Load Variable Library (CSV)
Resultado: generá 50 versiones distintas del mismo template
Uso: tarjetas de evento, posts con nombres, pricing cards
```

### Pixel Perfect en Illustrator

**Para que los vectores se vean nítidos en pantalla:**
```
Preferences > General > Align New Objects to Pixel Grid: ON
View > Pixel Preview: activar para verificar
Transform panel > Align to Pixel Grid en cada objeto
```

**Para texto nítido:**
```
Character panel > Anti-aliasing: Sharp (para texto pequeño)
Anti-aliasing: Crisp (para texto mediano)
Anti-aliasing: Strong (para texto grande/titulares)
```

---

## Sistema de templates en Adobe

### Estructura de carpetas recomendada

```
/[CLIENTE o MARCA]/
  /01-briefing/
  /02-referencias/
  /03-assets/
    /logos/           → vectores originales (.ai, .eps, .pdf, .svg)
    /fotos/           → originales sin editar
    /tipografias/     → archivos de fuente instalados
    /elementos/       → texturas, iconos, ilustraciones
  /04-produccion/
    /plantillas/      → archivos .psd y .ai maestros
    /en-progreso/     → WIPs
  /05-exportados/
    /instagram-feed/
    /instagram-stories/
    /facebook/
    /linkedin/
    /tiktok/
  /06-aprobados/
```

### Plantilla maestra en Photoshop

**Estructura de plantilla reutilizable:**
- Capas de ajuste al tope (no destructivas)
- Smart Objects para foto/producto: doble clic para reemplazar
- Texto en capas con estilo de párrafo/carácter guardado
- Guías en la zona segura de cada plataforma
- Artboard o Canvas configurado al tamaño exacto
- Color profile: sRGB embebido

---

## InDesign — Uso en social media

InDesign es ideal para:
- **Carruseles educativos en PDF** (LinkedIn, Instagram)
- **Documentos extensos** que se publican como PDF descargable
- **Producción en serie** de múltiples slides con consistencia tipográfica

### Configuración para carrusel social en InDesign

```
New Document:
  - Width: 1080px, Height: 1080px (o 1350px para 4:5)
  - Units: Pixels
  - Color Mode: RGB
  - Pages: número de slides del carrusel
  - Facing Pages: OFF

Preferences > Units & Increments:
  - Ruler Units: Pixels
```

**Estilos de párrafo para carrusel:**
```
Titular: 50pt Bold, tracking -10, leading 55pt
Subtítulo: 24pt Medium, tracking 0, leading 30pt
Body: 16pt Regular, tracking 0, leading 22pt
Bullet: 14pt Regular, tracking 0, leading 20pt, sangría 20px
Número estadística: 80pt ExtraBold, tracking -20, leading 80pt
Caption: 11pt Light, tracking +20, color 70% negro
```

**Exportar carrusel como imágenes:**
```
File > Export > JPEG o PNG
Pages: All
Resolution: 72 ppi (los px son lo que importa)
Color Space: RGB
Profile: sRGB
```

---

## Camera Raw / Lightroom — Edición de fotos para feed

### Perfil de edición base para consistencia de feed

**Configuración de perfil recomendada para feed lifestyle:**
```
Calibración:
  Perfil: Adobe Color o perfil neutro del fabricante

Tono básico:
  Exposure: 0 a +0.3 (ligeramente más brillante que la foto "real")
  Highlights: -30 a -60 (recuperar altas luces)
  Shadows: +20 a +40 (levantar sombras para más detalle)
  Whites: +10 a +20
  Blacks: -10 a -20 (más contraste en negros)
  
Presencia:
  Texture: +15 a +25
  Clarity: +5 a +15 (no exceder, crea halos)
  Vibrance: +15 a +25 (más sutil que Saturation)
  Saturation: 0 a +10
  
Curva de tono:
  Forma de S suave: levantar medios tonos, bajar levemente altas luces
  
HSL (para ajuste de colores específicos):
  Naranja/Rojo (pieles): Hue -3, Saturation -5, Luminance +5
  Cielo/Agua: Hue +5 en Azul, Saturation +10
```

**Guardar como preset:**
```
Preset panel > + > guardar como "Preset Base [Marca]"
Aplicar a todas las fotos del mismo cliente/feed
```

### Sincronizar edición entre fotos del feed

```
En Camera Raw / Lightroom:
1. Editar la foto piloto completamente
2. Seleccionar todas las fotos del lote
3. Sync Settings > seleccionar qué parámetros sincronizar
   (generalmente todo excepto Crop y Spot Removal)
```
