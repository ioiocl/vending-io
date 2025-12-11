# Guía de Uso de Webcam 📸

## Cómo Activar y Usar la Webcam

### Paso 1: Ejecutar el Juego
```powershell
python run_with_visualizer.py
```

### Paso 2: Abrir en Navegador
```
http://127.0.0.1:5000/game
```

### Paso 3: Activar Webcam
1. **Presiona la tecla `W`** en el juego
2. El navegador pedirá permiso para usar la cámara
3. **Haz clic en "Permitir"** o "Allow"

### Paso 4: Verificar que Funciona
- ✅ Video aparece en esquina inferior derecha
- ✅ Estado dice: "📸 Webcam: Active - Wave hand to spawn!"
- ✅ Puedes verte en el video (espejo)

### Paso 5: Generar Items
1. **Mueve tu mano** frente a la cámara
2. **Agita la mano** (movimiento rápido)
3. ⭐ **Estrella dorada aparece** en posición aleatoria
4. **Mueve al personaje** para recolectarla
5. **+50 puntos!**

## Solución de Problemas

### ❌ Webcam no se activa

**Problema:** Al presionar W no pasa nada

**Soluciones:**
1. **Verifica permisos del navegador:**
   - Chrome: Configuración → Privacidad → Cámara
   - Edge: Configuración → Permisos del sitio → Cámara
   - Firefox: Preferencias → Privacidad → Permisos

2. **Prueba en otro navegador:**
   - Chrome (recomendado)
   - Edge
   - Firefox

3. **Verifica que la cámara funciona:**
   - Abre la app de Cámara de Windows
   - Si funciona ahí, debería funcionar en el juego

### ❌ Video negro

**Problema:** Video aparece pero está negro

**Soluciones:**
1. **Cierra otras apps que usen la cámara:**
   - Zoom, Teams, Skype, etc.
   - Solo una app puede usar la cámara a la vez

2. **Recarga la página:**
   - Presiona `F5`
   - Presiona `W` de nuevo

3. **Reinicia el navegador:**
   - Cierra todas las pestañas
   - Abre de nuevo

### ❌ No detecta mi mano

**Problema:** Video funciona pero no genera items

**Soluciones:**
1. **Mueve la mano más rápido:**
   - El sistema detecta movimiento
   - Agita la mano de lado a lado
   - Muévela arriba y abajo

2. **Acércate más a la cámara:**
   - Debe estar en la mitad superior del video
   - A 30-50cm de la cámara

3. **Mejor iluminación:**
   - Enciende más luces
   - Evita contraluz (ventana detrás)

4. **Verifica en consola:**
   - Presiona `F12` en el navegador
   - Ve a la pestaña "Console"
   - Busca mensajes: "✋ Hand motion detected!"

### ❌ Genera items todo el tiempo

**Problema:** Aparecen muchas estrellas sin mover la mano

**Soluciones:**
1. **Quédate quieto:**
   - El sistema detecta cualquier movimiento
   - Mantén la mano fuera del cuadro

2. **Ajusta sensibilidad:**
   - Abre `game_visualizer.html`
   - Busca: `if (motion > 15`
   - Cambia `15` a `25` (menos sensible)
   - Cambia `15` a `10` (más sensible)

## Cómo Funciona

### Detección de Movimiento
```javascript
1. Captura frame actual de video
2. Compara con frame anterior
3. Calcula diferencia de píxeles
4. Si diferencia > 15 → Movimiento detectado
5. Espera 1.5 segundos antes de detectar de nuevo
```

### Zona de Detección
```
┌─────────────────────┐
│  ZONA ACTIVA (50%)  │ ← Aquí mueve la mano
│  Detecta movimiento │
├─────────────────────┤
│  ZONA INACTIVA      │
│  No detecta         │
└─────────────────────┘
```

## Tips para Mejor Detección

### ✅ Hacer
- ✅ Mueve la mano rápidamente
- ✅ Agita de lado a lado
- ✅ Mantén buena iluminación
- ✅ Acércate a la cámara
- ✅ Usa fondo simple

### ❌ Evitar
- ❌ Movimientos lentos
- ❌ Mano muy lejos
- ❌ Poca luz
- ❌ Contraluz
- ❌ Fondo con mucho movimiento

## Controles del Juego

| Tecla | Acción |
|-------|--------|
| **W** | Activar/Desactivar webcam |
| **F** | Modo vuelo |
| **Espacio** | Saltar / Volar |
| **←→** | Mover horizontal |
| **↑↓** | Volar vertical (en modo vuelo) |

## Información Técnica

### Requisitos
- ✅ Navegador moderno (Chrome, Edge, Firefox)
- ✅ Webcam conectada
- ✅ Permisos de cámara permitidos
- ✅ JavaScript habilitado

### Privacidad
- ✅ Todo se procesa localmente en tu navegador
- ✅ No se envía video al servidor
- ✅ No se graba nada
- ✅ Solo se detecta movimiento

### Rendimiento
- Detección cada 100ms (10 FPS)
- Analiza solo mitad superior del video
- Bajo uso de CPU
- No afecta el juego

## Ejemplos de Uso

### Ejemplo 1: Juego Normal
```
1. Presiona W → Webcam activa
2. Arduino genera pulsos → Saltas sobre ellos
3. Agitas mano → Estrella aparece
4. Recolectas estrella → +50 puntos
5. Sigues jugando → Más pulsos y estrellas
```

### Ejemplo 2: Modo Vuelo con Webcam
```
1. Presiona W → Webcam activa
2. Presiona F → Modo vuelo
3. Presiona Espacio → Empiezas a volar
4. Agitas mano → Estrella aparece arriba
5. Vuelas hacia ella → +50 puntos
6. Vuelas sobre pulsos → +10 puntos cada uno
```

### Ejemplo 3: Farming de Estrellas
```
1. Activa webcam
2. Agita mano cada 2 segundos
3. Múltiples estrellas aparecen
4. Vuela para recolectar todas
5. ¡Alto score!
```

## Ajustar Sensibilidad

Si quieres cambiar qué tan fácil es detectar la mano:

### Archivo: `web/templates/game_visualizer.html`

```javascript
// Línea ~906
if (motion > 15 && timeSinceLastDetection > 1500) {
    // Cambia estos valores:
    
    // motion > 15
    // - Más bajo (10) = Más sensible
    // - Más alto (25) = Menos sensible
    
    // timeSinceLastDetection > 1500
    // - Más bajo (1000) = Más frecuente
    // - Más alto (3000) = Menos frecuente
}
```

## Comandos de Consola

Abre la consola del navegador (F12) y prueba:

```javascript
// Ver estado de webcam
console.log(game.webcamActive);

// Forzar spawn de item
socket.emit('hand_raised', { x: 0.5, y: 0.5, timestamp: Date.now() });

// Ver nivel de movimiento actual
// (Aparece automáticamente cuando detecta)
```

---

**¡Disfruta jugando con la webcam!** 📸🌟🎮
