# Control Dinámico de Dificultad 🎚️

## Mecánica: Tu Mano Controla la Dificultad

### Concepto
**Mientras más cerca esté tu mano del sensor Arduino, más grandes y difíciles serán los pulsos en el juego.**

---

## 📏 Tabla de Dificultad

| Distancia | Intensidad | Altura Pulso | Velocidad | Dificultad | Color |
|-----------|------------|--------------|-----------|------------|-------|
| **5cm** (muy cerca) | 0.9 | ~260px | 6.7 px/f | **HARD!** 🔴 | Rojo |
| **10cm** (cerca) | 0.8 | ~240px | 6.4 px/f | **Hard** 🟠 | Naranja |
| **15cm** (medio) | 0.7 | ~220px | 6.1 px/f | **Medium** 🟡 | Amarillo |
| **25cm** (lejos) | 0.5 | ~180px | 5.5 px/f | **Easy** 🟢 | Verde |
| **35cm** (muy lejos) | 0.3 | ~140px | 4.9 px/f | **Very Easy** 🔵 | Cyan |
| **50cm+** (extremo) | 0.0 | ~80px | 4.0 px/f | **Very Easy** 💙 | Azul |

---

## 🎮 Visualización en Juego

### Pulso Fácil (Mano Lejos - 40cm)
```
                    40cm
                  Very Easy
┌────────────────────────────────────┐
│                                    │
│                                    │
│              ╔════╗                │
│              ║    ║ 80px           │
│              ║    ║ (bajo)         │
│   ╔══╗       ║    ║                │
│   ║🎮║       ║    ║                │
│   ╚══╝       ║    ║                │
│  ═══════════════════════════════   │
│                                    │
└────────────────────────────────────┘
```
- ✅ Altura: 80px (fácil de saltar)
- ✅ Velocidad: 4 px/frame (lento)
- ✅ Ancho: 25px (estrecho)
- ✅ Color: Cyan/Azul (suave)

### Pulso Medio (Mano Media - 15cm)
```
                    15cm
                   Medium
┌────────────────────────────────────┐
│                                    │
│              ╔══════╗              │
│              ║      ║              │
│              ║      ║              │
│              ║      ║ 220px        │
│              ║      ║ (medio)      │
│   ╔══╗       ║      ║              │
│   ║🎮║       ║      ║              │
│   ╚══╝       ║      ║              │
│  ═══════════════════════════════   │
│                                    │
└────────────────────────────────────┘
```
- ⚠️ Altura: 220px (desafiante)
- ⚠️ Velocidad: 6.1 px/frame (rápido)
- ⚠️ Ancho: 67px (medio)
- ⚠️ Color: Amarillo (advertencia)

### Pulso Difícil (Mano Cerca - 5cm)
```
                     5cm
                    HARD!
┌────────────────────────────────────┐
│              ╔════════╗            │
│              ║        ║            │
│              ║        ║            │
│              ║        ║            │
│              ║        ║            │
│              ║        ║ 260px      │
│              ║        ║ (MUY ALTO!)│
│   ╔══╗       ║        ║            │
│   ║🎮║       ║        ║            │
│   ╚══╝       ║        ║            │
│  ═══════════════════════════════   │
└────────────────────────────────────┘
```
- 🔴 Altura: 260px (casi imposible saltar!)
- 🔴 Velocidad: 6.7 px/frame (muy rápido)
- 🔴 Ancho: 79px (ancho)
- 🔴 Color: Rojo (peligro!)

---

## 🎯 Estrategias de Juego

### 1. **Principiante: Mantén Distancia**
```
Tu mano → [========== 40cm ==========] ← Sensor Arduino

Resultado:
- Pulsos pequeños y lentos
- Fácil de saltar
- Perfecto para aprender
```

### 2. **Intermedio: Varía la Distancia**
```
Tu mano → [==== 15-30cm ====] ← Sensor Arduino

Resultado:
- Pulsos medianos
- Velocidad moderada
- Balance entre desafío y diversión
```

### 3. **Experto: Acércate al Límite**
```
Tu mano → [= 5-10cm =] ← Sensor Arduino

Resultado:
- Pulsos ENORMES
- Velocidad máxima
- ¡Usa modo vuelo para sobrevivir!
```

### 4. **Maestro: Control Dinámico**
```
Lejos (40cm) → Pulso fácil → Saltas
     ↓
Cerca (8cm) → Pulso difícil → Usas modo vuelo
     ↓
Lejos (35cm) → Pulso fácil → Saltas de nuevo
     ↓
¡Controlas el ritmo del juego!
```

---

## 🔢 Fórmulas Implementadas

### Altura del Pulso
```javascript
baseHeight = 80px
maxHeightBonus = 200px
height = baseHeight + (intensity × maxHeightBonus)

Ejemplos:
- 5cm  → intensity 0.9 → 80 + (0.9 × 200) = 260px
- 15cm → intensity 0.7 → 80 + (0.7 × 200) = 220px
- 40cm → intensity 0.2 → 80 + (0.2 × 200) = 120px
```

### Velocidad del Pulso
```javascript
baseSpeed = 4 px/frame
maxSpeedBonus = 3 px/frame
speed = baseSpeed + (intensity × maxSpeedBonus)

Ejemplos:
- 5cm  → intensity 0.9 → 4 + (0.9 × 3) = 6.7 px/frame
- 15cm → intensity 0.7 → 4 + (0.7 × 3) = 6.1 px/frame
- 40cm → intensity 0.2 → 4 + (0.2 × 3) = 4.6 px/frame
```

### Ancho del Pulso
```javascript
baseWidth = 25px
maxWidthBonus = 60px
width = baseWidth + (intensity × maxWidthBonus)

Ejemplos:
- 5cm  → intensity 0.9 → 25 + (0.9 × 60) = 79px
- 15cm → intensity 0.7 → 25 + (0.7 × 60) = 67px
- 40cm → intensity 0.2 → 25 + (0.2 × 60) = 37px
```

### Intensidad (del Sensor)
```javascript
// Calculada en web_visualizer_adapter.py
max_distance = 50.0
intensity = 1.0 - (min(distance, max_distance) / max_distance)

Ejemplos:
- 5cm  → 1.0 - (5/50)  = 0.90 (90% intensidad)
- 15cm → 1.0 - (15/50) = 0.70 (70% intensidad)
- 25cm → 1.0 - (25/50) = 0.50 (50% intensidad)
- 50cm → 1.0 - (50/50) = 0.00 (0% intensidad)
```

---

## 🎨 Indicadores Visuales

### Etiquetas de Dificultad
El juego muestra automáticamente:

```javascript
if (intensity > 0.7)  → "HARD!"      (Rojo #ff4444)
if (intensity > 0.5)  → "Medium"     (Naranja #ffaa00)
if (intensity > 0.3)  → "Easy"       (Verde #00ff88)
else                  → "Very Easy"  (Cyan #00ffff)
```

### Efectos Visuales
- **Brillo (glow)**: Más intenso para pulsos difíciles
- **Gradiente**: De oscuro (arriba) a claro (abajo)
- **Color**: Cambia de cyan (fácil) a rojo (difícil)

---

## 💡 Tips Avanzados

### 1. **Modo Vuelo para Pulsos Difíciles**
```
Mano cerca (5cm) → Pulso ENORME aparece
     ↓
Presiona F → Modo vuelo
     ↓
Presiona Espacio → Empiezas a volar
     ↓
Vuela SOBRE el pulso gigante
     ↓
¡Sobrevives al desafío!
```

### 2. **Combo de Dificultad**
```
Pulso fácil (40cm)  → +10 pts × 1 = 10
Pulso medio (20cm)  → +10 pts × 2 = 20
Pulso difícil (8cm) → +10 pts × 3 = 30
                       Total: 60 puntos!
```

### 3. **Farming de Puntos**
```
1. Mantén mano lejos (40cm)
2. Genera muchos pulsos fáciles
3. Salta todos sin fallar
4. Construye combo alto
5. ¡Alto score!
```

### 4. **Desafío Extremo**
```
1. Mano muy cerca (5cm)
2. Pulsos gigantes
3. Usa modo vuelo obligatorio
4. Recolecta estrellas mientras vuelas
5. ¡Máxima dificultad!
```

---

## 🎓 Curva de Aprendizaje

### Nivel 1: Aprendiz (40-50cm)
- Pulsos pequeños
- Velocidad lenta
- Aprende controles básicos
- Objetivo: 100 puntos

### Nivel 2: Jugador (25-35cm)
- Pulsos medianos
- Velocidad moderada
- Practica timing de saltos
- Objetivo: 300 puntos

### Nivel 3: Experto (15-25cm)
- Pulsos grandes
- Velocidad rápida
- Usa modo vuelo ocasionalmente
- Objetivo: 600 puntos

### Nivel 4: Maestro (5-15cm)
- Pulsos enormes
- Velocidad máxima
- Modo vuelo esencial
- Objetivo: 1000+ puntos

### Nivel 5: Leyenda (Control Dinámico)
- Varía distancia constantemente
- Controla dificultad en tiempo real
- Combina saltos y vuelo perfectamente
- Objetivo: 2000+ puntos

---

## 📊 Comparación Visual

```
DISTANCIA vs DIFICULTAD

50cm ████░░░░░░ 10% (Muy Fácil)
40cm ██████░░░░ 20% (Muy Fácil)
30cm ████████░░ 40% (Fácil)
20cm ██████████ 60% (Medio)
15cm ████████████ 70% (Medio-Difícil)
10cm ██████████████ 80% (Difícil)
5cm  ████████████████ 90% (MUY DIFÍCIL!)
```

---

## 🎮 Ejemplo de Sesión de Juego

```
Tiempo  Distancia  Pulso      Acción           Resultado
─────────────────────────────────────────────────────────
0:00    40cm       Pequeño    Salto normal     +10 pts
0:03    35cm       Pequeño    Salto normal     +20 pts (x2)
0:06    20cm       Mediano    Salto alto       +30 pts (x3)
0:09    15cm       Grande     Salto perfecto   +40 pts (x4)
0:12    8cm        ENORME     Activa vuelo     +50 pts (x5)
0:15    5cm        GIGANTE    Vuela sobre él   +60 pts (x6)
0:18    30cm       Mediano    Salto normal     +70 pts (x7)
─────────────────────────────────────────────────────────
Total: 280 puntos en 18 segundos!
```

---

## 🔧 Ajustar Dificultad (Opcional)

Si quieres cambiar la dificultad, edita `game_visualizer.html`:

```javascript
// Línea ~317-329
// Hacer más fácil:
const maxHeightBonus = 150;  // (antes: 200)
const maxSpeedBonus = 2;     // (antes: 3)

// Hacer más difícil:
const maxHeightBonus = 250;  // (antes: 200)
const maxSpeedBonus = 4;     // (antes: 3)
```

---

**¡Ahora controlas la dificultad del juego con tu mano! Acércala para más desafío, aléjala para más facilidad.** 🎚️🎮✨
