# 04 — Color para Redes Sociales

## Fundamentos de color en diseño digital

### Modos de color en Adobe para social media

```
SIEMPRE trabajar en: RGB (no CMYK)
Espacio de color: sRGB IEC61966-2.1
Profundidad: 8 bits (16 bits para edición de foto, convertir antes de exportar)
```

**Por qué sRGB y no Display P3 o Adobe RGB:**
- Los navegadores y redes sociales interpretan imágenes en sRGB por defecto
- P3 y Adobe RGB pueden verse desaturados o incorrectos si la plataforma no honra el perfil ICC
- Excepción: si tu audiencia usa dispositivos Apple recientes y trabajás en Ps con exportación específica

---

## Teoría del color aplicada

### Armonías cromáticas y su efecto en social

#### Monocromático
- Un solo tono en diferentes saturaciones y valores
- Efecto: sofisticación, cohesión, minimalismo
- Uso: branding premium, contenido editorial, reels de alta producción
- Riesgo: puede volverse monótono sin variación de valor suficiente

#### Análogo
- 2–3 colores adyacentes en el círculo cromático (±30°)
- Efecto: armonía natural, confort, fluidez
- Uso: lifestyle, bienestar, contenido educativo
- Aplicación en social: fondo análogo claro + acento análogo oscuro + texto neutro

#### Complementario
- Colores opuestos en el círculo (180°)
- Efecto: alto contraste, energía, impacto visual inmediato
- Uso: ofertas, lanzamientos, contenido deportivo
- Riesgo: puede volverse agresivo → usar 70% de un color, 30% del complementario

**Pares complementarios populares en social media:**
```
Azul + Naranja:   confianza + energía (muy común en tech y finanzas)
Púrpura + Amarillo: creatividad + optimismo (educación, entretenimiento)
Verde + Rojo:     natural + urgencia (salud, food, promos)
```

#### Triádico
- 3 colores equidistantes (120° entre sí)
- Efecto: vibrante, dinámico, versátil
- Uso: marcas jóvenes, entretenimiento, apps
- Regla de aplicación: 60% dominante, 30% secundario, 10% acento

#### Split-complementario
- Un color base + dos colores adyacentes a su complementario
- Más sutil que el complementario puro, más contraste que el análogo
- Ideal para social cuando se necesita impacto sin agresividad

---

## Psicología del color para social media

| Color | Percepción | Industrias | Evitar en |
|---|---|---|---|
| Azul | Confianza, profesionalismo, calma | Finanzas, tech, salud, corporativo | Comida (suprime apetito) |
| Rojo | Urgencia, pasión, energía, peligro | Ofertas, food, deporte, entretenimiento | Bienestar, lujo premium |
| Naranja | Entusiasmo, creatividad, accesibilidad | Retail, comida rápida, startups | Lujo, corporativo formal |
| Amarillo | Optimismo, atención, calidez | Niños, comida, promocs, energía | Finanzas serias, salud |
| Verde | Naturaleza, salud, dinero, equilibrio | Sustentabilidad, salud, finanzas, food | Tecnología (a menos que sea intencional) |
| Púrpura | Creatividad, lujo, espiritualidad | Belleza, educación, entretenimiento | Comida rápida, deporte |
| Negro | Sofisticación, poder, elegancia | Moda, lujo, tech premium | Niños, salud, food |
| Blanco | Limpieza, simplicidad, espacio | Todas las industrias como neutro | Como único color (invisible) |
| Rosa | Ternura, romance, feminidad | Belleza, moda, lifestyle femenino | Industrias "serias" sin intención |

---

## Sistemas de color para marca en redes sociales

### Estructura de paleta recomendada

```
Color Primario (1):    El color dominante de la marca — 50–60% de presencia
Color Secundario (1):  Complementa o análogo — 20–30% de presencia  
Color de Acento (1):   Alto contraste, solo para CTAs y highlights — 5–10%
Neutros (2–3):         Blancos, grises, negros para texto y fondos — 10–20%
```

### Cómo definir los valores en Adobe

**Al crear una paleta, siempre documentar:**
```
Nombre: Azul Primario
HEX: #1A3C6E
RGB: R:26 G:60 B:110
HSB: H:215° S:76% B:43%
Pantone: 294 C (si hay necesidad de impresión)
Uso: fondos de sección, botones primarios, headers
```

---

## Contraste y accesibilidad

### WCAG (Web Content Accessibility Guidelines)

**Ratios de contraste mínimos:**
```
WCAG AA — Texto normal (<18px): 4.5:1
WCAG AA — Texto grande (>18px bold o >24px): 3:1
WCAG AAA — Texto normal: 7:1
WCAG AAA — Texto grande: 4.5:1
```

**Cómo calcular en Adobe:**
- Photoshop: Plugin Stark o verificar con cuentagotas ambos colores
- Illustrator: Edit > Edit Colors > Adjust Color Balance
- Herramienta web: contrast-ratio.com o colorsafe.co

**Paletas de contraste garantizado para texto blanco:**
```
#1A1A2E  (azul muy oscuro)     Ratio vs blanco: 16:1 ✓✓
#2D3436  (gris oscuro)         Ratio vs blanco: 12:1 ✓✓
#6C3483  (púrpura oscuro)      Ratio vs blanco: 7:1  ✓
#1B4F72  (azul marino)         Ratio vs blanco: 8:1  ✓
#922B21  (rojo oscuro)         Ratio vs blanco: 7:1  ✓
```

**Paletas de contraste garantizado para texto negro:**
```
#FDFEFE  (blanco puro)         Ratio vs negro: 21:1 ✓✓
#F9E79F  (amarillo claro)      Ratio vs negro: 12:1 ✓✓
#A9DFBF  (verde menta)         Ratio vs negro: 8:1  ✓
#85C1E9  (azul cielo)          Ratio vs negro: 5:1  ✓
```

---

## Tendencias de color 2024–2025 en social media

### Paletas que dominan el feed

#### Neo-Brutalism
```
Fondo: #FFEB3B (amarillo) o #FF6B6B (coral)
Texto: #000000
Acento: #FFFFFF
Bordes: negros, 3–4px sólido
```

#### Dopamine Design (colores maximales)
```
Estilo: saturación al máximo, sin miedo al color
Combinaciones: análogos altamente saturados
Típico: azul eléctrico + verde lima + amarillo neón
```

#### Digital Minimalism
```
Fondo: #F5F5F0 (off-white cálido)
Texto: #1A1A1A
Acento: 1 color saturado en 10% de la superficie
Mucho espacio negativo
```

#### Earth Tones Modernos
```
Terracota: #C25B3F
Sage: #87A878
Beige: #E8D5C4
Marrón oscuro: #3E2723
```

---

## Color en Photoshop — Técnicas avanzadas

### Grading de color para consistencia de feed

**Lookup Tables (LUTs) para feed coherente:**
```
Layer > New Adjustment Layer > Color Lookup
Aplicar el mismo LUT a todos los posts del mes
Guardar el archivo .CUBE para reutilizar
```

**Técnica de color matching entre fotos:**
```
Edit > Match Color
Source: foto de referencia
Luminance/Color Intensity/Fade: ajustar según la foto
```

**Gradient Maps para tonos de marca:**
```
Layer > New Adjustment Layer > Gradient Map
Definir degradado de oscuro a claro con los colores de marca
Opacidad: 10–30% (modo Color o Soft Light)
Resultado: todas las fotos adquieren el tono de la paleta de marca
```

### Corrección de color para redes sociales

**Las redes sociales comprimen y alteran el color al subir:**
- Instagram comprime JPEG con calidad variable
- TikTok aplica su propio procesamiento de color
- LinkedIn altera menos pero sigue comprimiendo

**Compensación:**
- Subir saturation +5 a +10 antes de exportar
- Subir clarity/texture levemente para contrarrestar suavizado
- Exportar como sRGB siempre
- Para Instagram: exportar como PNG para fondos de color plano, JPEG para fotos

---

## Color en Illustrator — Swatches y bibliotecas

### Crear biblioteca de colores de marca

```
Window > Swatches > menú hamburguesa > Add Selected Colors
Guardar como: Adobe Swatch Exchange (.ase)
Compartir .ase con el equipo o usar Libraries de Creative Cloud
```

### Global Colors en Illustrator
```
Doble clic en swatch > marcar "Global"
Beneficio: cambiar el swatch actualiza TODOS los objetos que lo usan
Indispensable para adaptar piezas entre clientes
```
