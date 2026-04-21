# 03 — Tipografía para Redes Sociales

## Principios de tipografía en digital/social

### Escala tipográfica para social media

La escala modular más usada en diseño social es **1.25 (Major Third)** o **1.333 (Perfect Fourth)**.

**Escala base 16px con ratio 1.333:**
```
xs:  10px  → captions, créditos, disclaimers
sm:  13px  → body secundario, datos
base: 16px → body principal
md:  21px  → subtítulos, lead
lg:  28px  → títulos secundarios
xl:  37px  → títulos principales
2xl: 50px  → display, hero text
3xl: 67px  → grandes titulares (Stories, thumbnails)
4xl: 89px  → tipografía como elemento visual
```

**Regla de legibilidad en mobile:**
- Tamaño mínimo cuerpo de texto: 14px a resolución 1× (28px en documento 2×)
- Tamaño mínimo para texto de relleno/disclaimers: 10px
- CTA / texto de acción: nunca menos de 16px

---

### Categorías tipográficas y su uso en social

#### Serif
**Personalidad:** autoridad, tradición, lujo, editorial
**Plataformas donde funciona:** LinkedIn, Instagram feed de marcas premium, Pinterest
**Pares bien con:** sans-serif geométrica limpia
**Ejemplos de uso:** titulares de artículos, quotes de líderes, contenido de moda/lifestyle

**Fuentes serif recomendadas:**
- Playfair Display — elegancia, contraste de trazo dramático
- Libre Baskerville — editorial, accesible
- Cormorant Garamond — lujo máximo, poca legibilidad a tamaños pequeños
- Lora — legible, versátil para body text
- DM Serif Display — moderno pero clásico

#### Sans-serif geométrica
**Personalidad:** modernidad, tech, minimalismo, confianza
**Plataformas donde funciona:** todas, especialmente Instagram y LinkedIn
**Pares bien con:** serif contrastante o monospace
**Ejemplos de uso:** todo tipo de contenido, especialmente educativo e informativo

**Fuentes geométricas recomendadas:**
- Inter — máxima legibilidad en pantalla, pesos completos
- DM Sans — moderna, accesible
- Nunito — amigable, redondeada
- Poppins — popular en redes, geométrica pura
- Plus Jakarta Sans — premium, excelente en titulares

#### Display / Decorativa
**Personalidad:** identidad fuerte, impacto visual, entretenimiento
**Uso:** solo para titulares muy grandes, nunca para body
**Riesgo:** legibilidad reducida, envejecimiento rápido

**Fuentes display para social:**
- Cabinet Grotesk — actual, editorial
- Clash Display — impacto, muy usada en 2024–2025
- General Sans — neutral pero con carácter

---

### Combinaciones tipográficas para social media

#### Combinación 1: Autoridad + Claridad
```
Titular: Playfair Display Bold — 50–89px
Subtítulo: Inter SemiBold — 21–28px
Body: Inter Regular — 14–16px
Acento: Playfair Display Italic — mismo tamaño que subtítulo
```

#### Combinación 2: Tech / Startup / SaaS
```
Titular: Plus Jakarta Sans ExtraBold — 40–67px
Subtítulo: Plus Jakarta Sans Medium — 18–24px
Body: Inter Regular — 14–16px
Datos/Stats: Plus Jakarta Sans Bold — 50–89px (números grandes)
```

#### Combinación 3: Lifestyle / Marca personal
```
Titular: Cormorant Garamond Light Italic — 50–89px
Subtítulo: DM Sans Medium — 18–24px
Body: DM Sans Regular — 14–16px
Quote: Cormorant Garamond Regular — 24–37px
```

#### Combinación 4: Contenido educativo / Infografías
```
Titular: Poppins Bold — 28–50px
Subtítulo: Poppins SemiBold — 18–21px
Body: Poppins Regular — 14–16px
Datos: Poppins ExtraBold — 50–89px
Labels: Poppins Medium — 12–14px
```

---

### Jerarquía tipográfica en piezas sociales

**Modelo de 3 niveles:**
```
Nivel 1 (HERO):    Texto que detiene el scroll — 1 elemento
                   Tamaño: xl a 4xl según formato
                   Peso: Bold o ExtraBold
                   
Nivel 2 (APOYO):   Contexto o subtítulo — 1–2 líneas
                   Tamaño: md a lg
                   Peso: Regular a Medium
                   
Nivel 3 (DETALLE): Body, disclaimer, crédito
                   Tamaño: xs a base
                   Peso: Regular, reducido en opacidad (60–70%)
```

---

### Tracking y Leading en social media

**Leading (interlineado):**
- Titulares grandes (>40px): 1.0–1.1 (más comprimido para impacto)
- Subtítulos (20–40px): 1.2–1.35
- Body text (<20px): 1.4–1.6 (necesita aire para legibilidad)

**Tracking (espaciado de letras):**
- Titulares uppercase: +50 a +150 unidades (ampliar para impacto)
- Titulares normales: -10 a 0 (ligeramente comprimido)
- Body: 0 a +10 (no modificar o mínimo positivo)
- Mayúsculas en labels/tags: +100 a +200

---

### Texto sobre imagen — Técnicas avanzadas en Photoshop/Illustrator

#### 1. Overlay de degradado
```
Capa nueva por encima de la foto
Modo: Multiplicación o Normal
Degradado: Negro 0% a Negro 70%
Dirección: según dónde esté el texto (inferior para subtítulos)
```

#### 2. Texto con blending mode
```
Texto en blanco → Modo: Superposición (Overlay)
Funciona solo con fondos de contraste
Crea efecto integrado y sofisticado
```

#### 3. Clipping mask tipográfica
```
Imagen → Capa encima con Clipping Mask sobre texto
El texto actúa como máscara → la imagen aparece dentro de las letras
Ideal para titulares hero en Stories
```

#### 4. Desenfoque de fondo local
```
Duplicar capa de fondo
Gaussian Blur: 20–40px
Máscara de capa: ocultar todo, pintar solo la zona del texto
Resultado: texto sobre zona desenfocada, sujeto principal en foco
```

---

### Tipografía para cada plataforma

| Plataforma | Tamaño mínimo | Estilo que funciona | Evitar |
|---|---|---|---|
| Instagram feed | 28px en doc 1080px | Geométrica, serif editorial | Scripts ilegibles, más de 2 fuentes |
| Instagram Stories | 40px en doc 1080px | Cualquiera con buen contraste | Fuentes muy delgadas sobre foto |
| TikTok | 50px en doc 1080px | Bold, impacto visual | Serif finas, texto largo |
| LinkedIn | 24px en doc 1200px | Sans-serif profesional | Decorativas, informal |
| Pinterest | 32px en doc 1000px | Mix serif + sans | Texto excesivo en la imagen |
| YouTube thumbnail | 60px en doc 1280px | ExtraBold con stroke | Más de 6 palabras |

---

### Errores tipográficos frecuentes en social media

1. **Widows y orphans:** evitar que la última línea de un párrafo quede con una sola palabra
2. **Más de 2 familias tipográficas:** crear ruido visual
3. **Todos los pesos iguales:** sin contraste, sin jerarquía
4. **Texto muy centrado en párrafos largos:** dificulta la lectura, usar solo en 1–2 líneas
5. **Ignorar el kerning en titulares grandes:** los pares AV, WA, To, etc. necesitan ajuste manual
6. **Usar negrita de sistema:** siempre usar el peso Bold real de la fuente, no el bold sintético
7. **Mezclar mayúsculas y minúsculas arbitrariamente:** definir una regla y mantenerla
