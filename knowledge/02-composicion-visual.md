# 02 — Composición Visual para Redes Sociales

## Principios fundamentales aplicados a social media

### 1. Jerarquía visual
El ojo recorre la imagen en un orden determinado. En social media tenés 1–3 segundos para captar atención.

**Orden de peso visual (de mayor a menor):**
1. Movimiento / animación
2. Rostros humanos (especialmente ojos)
3. Texto grande / alto contraste
4. Color saturado sobre neutro
5. Formas geométricas simples
6. Texto pequeño / bajo contraste

**Aplicación práctica:**
- El elemento más importante debe tener el mayor peso visual
- Máximo 3 niveles de jerarquía por pieza
- Si todo grita, nada se escucha

---

### 2. Regla de los tercios en social media

**Grid 3×3 para contenido vertical (1080×1920):**
- Líneas verticales en: x=360 y x=720
- Líneas horizontales en: y=640 y y=1280
- Puntos de poder (intersecciones): (360,640), (720,640), (360,1280), (720,1280)

**Aplicación por formato:**
- Feed cuadrado: rostro/producto en punto de poder superior
- Stories: CTA siempre en tercio inferior, nunca en zona de UI
- Carrusel: elemento narrativo atraviesa el grid de forma consistente entre slides

---

### 3. Espacio negativo (breathing room)

En social media el espacio vacío es señal de calidad de marca.

**Márgenes mínimos recomendados:**
- Feed cuadrado (1080×1080): 54 px (5% del ancho)
- Stories (1080×1920): 60 px laterales, 250 px superior e inferior
- LinkedIn (1200×627): 60 px en todos los bordes

**Error común:** rellenar toda la superficie disponible. Las marcas premium usan 30–50% de espacio negativo.

---

### 4. Dirección y flujo visual

**Vectores de atención:**
- Las líneas diagonales crean dinamismo y urgencia (útil para offers, lanzamientos)
- Las líneas horizontales transmiten calma y estabilidad (ideal para branding lifestyle)
- Las líneas verticales sugieren crecimiento, aspiración
- Los arcos y curvas guían suavemente al siguiente elemento

**Regla de la mirada:** si hay un rostro en la imagen, el ojo del espectador sigue la dirección en que mira ese rostro. Colocar el CTA o texto clave en esa dirección.

---

### 5. Contraste y legibilidad en scroll

El feed se escanea rápido. El diseño debe funcionar a:
- Thumbnail: 150×150 px (perfil, preview)
- Mobile feed: aprox. 375 px de ancho
- Full screen: 1080 px

**Técnicas para garantizar legibilidad:**
```
Overlay semitransparente: fondo negro 40–60% de opacidad sobre foto
Drop shadow en texto: distancia 0, spread 0–2px, size 8–15px, opacidad 60–80%
Contorno de texto (stroke): 1–3px del color contrario
Área sólida detrás del texto: caja de color con padding 12–24px
Blur de fondo local (Gaussian Blur 15–30px en capa separada)
```

---

### 6. Composición para carrusel

El carrusel es el formato con mayor tiempo de engagement. Principios:

**Narrativa visual:**
- Slide 1: hook (problema, pregunta, dato impactante) — debe detener el scroll
- Slides 2–N: desarrollo (contenido de valor, pasos, argumentos)
- Slide final: CTA claro + refuerzo de marca

**Consistencia visual entre slides:**
- Mismo margen de contenido en todas las slides
- Elemento anclado: franja de color, logo, borde que se repita
- Si la relación es 4:5 (1080×1350), los márgenes laterales quedan expuestos al pasar slide → diseñar el 10% lateral como zona de transición

**Efecto panorámico en carrusel:**
- Crear un documento de 1080×N (ej. 5400px de ancho para 5 slides)
- Cada slide es una ventana de 1080 px de ancho
- El fondo/imagen se extiende de forma continua

---

### 7. Focal point y simplicidad

**Regla de un mensaje por pieza:**
Una imagen de redes sociales debe comunicar UNA sola idea.
Si hay que leerlo dos veces para entenderlo, ya perdiste al espectador.

**Test del 3 segundos:** mostrá el diseño 3 segundos y preguntá "¿qué decía?". Si la respuesta es vaga o incorrecta, simplificar.

---

### 8. Composición para Stories/Reels (formato vertical)

**Zonas de diseño (1080×1920):**
```
[0–250px]     Zona peligrosa superior (UI: reloj, batería, progreso)
[250–450px]   Zona de header / logo / hook visual
[450–1100px]  Zona de contenido principal (golden zone)
[1100–1490px] Zona secundaria / subtítulo / datos
[1490–1670px] Zona de CTA / stickers interactivos
[1670–1920px] Zona peligrosa inferior (UI: usuario, botones)
```

**Composición recomendada Stories:**
- Logo: esquina superior izquierda en y=260–280 (debajo de la zona peligrosa)
- Elemento hero (imagen/producto): ocupa el 40–60% de la zona central
- Texto principal: en la golden zone, con overlay si hay foto de fondo
- CTA: siempre como elemento separado visualmente (botón, flecha, sticker)

---

### 9. Simetría vs. Asimetría

**Simetría:** transmite equilibrio, lujo, formalidad. Ideal para fashion, cosmética, real estate.
**Asimetría:** transmite dinamismo, creatividad, modernidad. Ideal para tech, entretenimiento, sport.

**Equilibrio visual asimétrico:**
Un objeto grande a la izquierda se equilibra con múltiples objetos pequeños a la derecha, o con un elemento de alto contraste (texto, color).

---

### 10. Composición para thumbnails de YouTube

El thumbnail compite con cientos en la pantalla. Debe:
1. Funcionar en blanco y negro (contraste estructural, no dependiente del color)
2. Tener un punto focal dominante (rostro, número, objeto)
3. El texto debe ser legible a 168px de ancho (tamaño mínimo de visualización)
4. Evitar bordes: se cortan en algunos dispositivos

**Composición probada:**
- Rostro en 2/3 izquierdo, texto en 1/3 derecho (o viceversa)
- Número/dato grande + contexto corto
- Contraste extremo entre sujeto y fondo
