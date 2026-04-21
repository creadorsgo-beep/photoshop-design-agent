# 07 — Sistemas de Diseño para Redes Sociales

## Qué es un sistema de diseño para social media

Un sistema de diseño para social media es el conjunto de reglas, componentes y decisiones
documentadas que garantizan que cualquier pieza producida —independientemente de quién la haga—
sea reconocible como parte de la misma marca.

**Componentes del sistema:**
1. Tokens de diseño (color, tipografía, espaciado)
2. Componentes visuales reutilizables
3. Plantillas por formato
4. Reglas de uso y excepciones
5. Ejemplos de uso correcto e incorrecto

---

## Tokens de diseño — la capa base

### Token de color
```
// Paleta primaria
--color-brand-primary: #1A3C6E;
--color-brand-secondary: #E8A838;
--color-brand-accent: #E63946;

// Neutros
--color-neutral-100: #FFFFFF;
--color-neutral-200: #F5F5F5;
--color-neutral-500: #9E9E9E;
--color-neutral-900: #1A1A1A;

// Semánticos
--color-success: #2ECC71;
--color-warning: #F39C12;
--color-error: #E74C3C;
```

### Token de tipografía
```
// Familias
--font-primary: "Inter", sans-serif;
--font-display: "Playfair Display", serif;

// Pesos
--font-weight-regular: 400;
--font-weight-medium: 500;
--font-weight-semibold: 600;
--font-weight-bold: 700;
--font-weight-extrabold: 800;

// Escala (en px, para documento 1080px)
--text-xs: 10px;
--text-sm: 13px;
--text-base: 16px;
--text-md: 21px;
--text-lg: 28px;
--text-xl: 37px;
--text-2xl: 50px;
--text-3xl: 67px;
--text-hero: 89px;
```

### Token de espaciado (grid base 8px)
```
--space-1: 8px;
--space-2: 16px;
--space-3: 24px;
--space-4: 32px;
--space-6: 48px;
--space-8: 64px;
--space-12: 96px;
--space-16: 128px;

// Márgenes de contenido por formato
--margin-feed-square: 54px;    // 5% de 1080px
--margin-feed-vertical: 54px;
--margin-stories-horizontal: 60px;
--margin-stories-vertical-safe: 250px;
```

---

## Componentes visuales reutilizables

### 1. Header de marca (Stories)
```
Posición: y=260–310px (debajo de zona de UI)
Componentes: Logo + Handle + Separador visual
Variantes:
  - Sobre fondo claro: logo versión oscura
  - Sobre fondo oscuro: logo versión clara
  - Sobre foto: logo versión blanca + sombra
Tamaño logo: 80–120px de altura
```

### 2. Caja de texto (Text Box)
```
Propósito: legibilidad de texto sobre imagen
Variantes:
  a) Sólida: fondo de color de marca, sin transparencia
  b) Semi-transparente: fondo negro 60% o blanco 80%
  c) Blur: fondo difuminado del elemento de fondo
  d) Sin caja: texto con drop shadow o stroke

Padding estándar: 16px horizontal, 12px vertical
Border radius: 0 (formal), 8px (moderno), 100px (pastilla para tags)
```

### 3. Chip / Tag
```
Propósito: categorizar contenido, destacar temas
Estructura: [Icono opcional] + [Texto corto]
Tamaño de texto: 11–13px, peso Medium
Padding: 8px horizontal, 6px vertical
Formas: rectangular, redondeado, pastilla
Variantes de color: primario, secundario, ghost (solo borde)
```

### 4. Barra de progreso (Carrusel)
```
Propósito: indicar posición en carrusel
Posición: y=1840–1860px en Stories
Estilo: puntos circulares, barras lineales, número "X/Y"
Tamaño punto: 6–8px, activo: 8–10px
Color: blanco sobre fondos oscuros, oscuro sobre fondos claros
```

### 5. CTA Button
```
Variantes:
  Primario: fondo de color de acento, texto blanco/negro según contraste
  Secundario: borde de color, texto de color, sin relleno
  Texto: solo texto con flecha o icono
  
Tamaño: altura mínima 48px (área táctil accesible)
Texto: 14–16px, peso SemiBold o Bold
Padding: 16–24px horizontal, 12–16px vertical
Border radius: según personalidad de marca (0–100px)
```

### 6. Sello / Badge
```
Propósito: destacar ofertas, novedades, validaciones
Formas: circular, estrella, hexagonal, explosión
Tamaño: 120–200px en feed, 180–280px en stories
Rotación: -15° a +15° (da dinamismo)
Texto: corto, máximo 3 palabras en 2 líneas
```

---

## Plantillas por formato

### Estructura de plantilla en Photoshop

**Plantilla Feed Cuadrado (1080×1080px):**
```
Capa: REEMPLAZAR FOTO (Smart Object)
Capa: REEMPLAZAR TITULAR (Texto editable)
Capa: REEMPLAZAR SUBTÍTULO (Texto editable)
Grupo: MARCA (logo + handle — no editar)
Grupo: AJUSTES COLOR (capas de ajuste — no destructivo)
Guías: en zona segura (54px desde cada borde)
```

**Plantilla Stories (1080×1920px):**
```
Capa: REEMPLAZAR FONDO (Smart Object)
Grupo: ZONA SUPERIOR (logo + handle — y=260 a y=380)
Grupo: ZONA CONTENIDO (y=450 a y=1490)
  Capa: REEMPLAZAR TÍTULO
  Capa: REEMPLAZAR CUERPO
Grupo: ZONA CTA (y=1490 a y=1670)
  Capa: BOTÓN CTA
Guías rojas: en y=250 y y=1670 (zonas peligrosas)
Guías azules: zona segura lateral x=60 y x=1020
```

---

## Reglas de marca aplicadas a social

### Logo — reglas de uso
```
Espacio de protección: mínimo igual al ancho de la "M" del logo en todos los lados
Tamaño mínimo digital: 80px de altura (verificar legibilidad)
Versiones requeridas: positivo, negativo, solo ícono, solo texto
Fondos prohibidos: colores similares al logo, texturas muy complejas
Fondo sobre foto: aplicar fondo blanco semitransparente o usar versión blanca
```

### Fotografía — reglas de estilo
```
Temperatura de color: definir una temperatura consistente (cálida, neutra o fría)
Exposición: siempre bien iluminado, evitar fotos subexpuestas
Composición: siempre con espacio para superponer texto (si es necesario)
Personas: mostrar diversidad si la marca lo requiere, evitar fotos de stock genérico
Orientación: definir si el feed prioriza horizontal, vertical o cuadrado
```

### Ilustración y grafismo — reglas
```
Estilo: definir ONE style (flat, outline, 3D, pixel, orgánico) y mantenerlo
Peso de línea: consistente en todos los iconos e ilustraciones
Relleno vs. outline: elegir uno o definir cuándo usar cada uno
Perspectiva: isométrica, plana o libre — una sola
```

---

## Feed planning — consistencia visual

### Grillas de feed en Instagram

**Grilla de tablero (cada 3 posts):**
```
Post 1: Imagen oscura / Texto
Post 2: Imagen clara / Foto
Post 3: Color de marca / Gráfico
(repetir patrón)
```

**Grilla en franjas (de arriba a abajo):**
```
Fila 1: Color marca — Foto — Color marca
Fila 2: Foto — Color marca — Foto
(alternando)
```

**Grilla de rompecabezas:**
```
Una imagen grande se divide en 3 o 6 posts
Se ven como piezas separadas individualmente
Juntas forman una composición completa
Riesgo: muy complejo de mantener en el tiempo
```

### Paleta de contenidos recomendada (mix mensual)
```
40% — Contenido educativo / de valor
25% — Contenido de marca / storytelling
20% — Contenido de producto / servicio
15% — Contenido de comunidad / UGC / interacción
```

---

## Documentación del sistema

### Qué documentar para cada cliente/marca

```
1. PALETA DE COLOR
   - Valores HEX, RGB, HSB de cada color
   - Nombre del color en el sistema (no "azul", sino "Ocean Primary")
   - Cuándo usar cada uno

2. TIPOGRAFÍA
   - Familias y dónde descargarlas/licenciarlas
   - Jerarquía: qué fuente + peso para cada nivel
   - Tamaños mínimos y máximos por formato

3. LOGOS
   - Archivos fuente (AI, EPS, SVG, PDF vectorial)
   - Versiones disponibles
   - Reglas de uso y prohibiciones

4. COMPONENTES
   - Capturas de cada componente
   - Especificaciones técnicas
   - Variantes y cuándo usarlas

5. EJEMPLOS
   - Piezas aprobadas por categoría
   - Ejemplos de USO INCORRECTO (igual de importante)

6. PLANTILLAS
   - Archivos .psd y .ai por formato
   - Instrucciones de edición
   - Notas sobre qué es editable y qué no
```

---

## Automatización con Adobe Scripts

### Script Photoshop: Cambiar texto en múltiples archivos
```javascript
// Abrir en Script Editor: File > Scripts > Script Editor
// O guardar como .jsx y ejecutar vía File > Scripts > Browse

var folderPath = Folder.selectDialog("Seleccionar carpeta de PSDs");
var fileList = folderPath.getFiles("*.psd");

for (var i = 0; i < fileList.length; i++) {
    var doc = app.open(fileList[i]);
    
    // Encontrar capa de texto por nombre
    var layer = doc.layers.getByName("TITULAR");
    if (layer.kind == LayerKind.TEXT) {
        layer.textItem.contents = "Nuevo texto aquí";
    }
    
    // Guardar y cerrar
    doc.save();
    doc.close();
}
```

### Action Set recomendado para social media
```
Set: "Social Media Production"
  Action: Exportar feed JPEG
  Action: Exportar stories PNG
  Action: Exportar pack completo
  Action: Redimensionar para LinkedIn
  Action: Preparar foto (Camera Raw + ajustes base)
  Action: Agregar LUT de marca
  Action: Máscara de recorte circular (avatares)
```
