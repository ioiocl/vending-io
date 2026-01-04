# Music-IO 🎮

**Interactive Gaming Machine with Robotic Prize Delivery** - Una máquina de juegos interactiva que combina un juego web con un brazo robótico real que entrega premios físicos.

## 🎯 ¿Qué es Music-IO?

Music-IO es una **máquina de juegos arcade moderna** construida con arquitectura hexagonal que:

1. 👋 **Te detecta** cuando te acercas (sensor de proximidad)
2. 🎮 **Te invita** a jugar con un mensaje en pantalla
3. 🔘 **Inicia el juego** cuando presionas el botón físico
4. 🏃 **Te reta** a sobrevivir 60 segundos esquivando enemigos
5. 🤖 **Te premia** con un objeto real entregado por un brazo robótico
6. 🎫 **Te imprime** un recuerdo en papel térmico

### Características Actuales

- **Sensor de Proximidad**: Detecta jugadores a menos de 50cm e invita a jugar
- **Botón Físico**: Inicia el juego con efectos de luz y danza de servos
- **Juego Web**: Navegador con controles de teclado, joystick USB o gestos con cámara
- **Brazo Robótico**: Sistema multi-servo (SG90, DS04-NFC 360°, KS3518) con secuencias coreografiadas
- **Sistema de Succión**: Bomba de vacío para agarrar y entregar objetos
- **Impresora Térmica**: Imprime recuerdos personalizados con ASCII art y poemas generados por IA
- **Visualizador Web**: Dashboard en tiempo real con WebSocket
- **Arquitectura Modular**: Sistema de 2 etapas (COM7 y COM4) con comunicación serial

### Arquitectura del Sistema

```
┌──────────────────────────────────────────────────────────────┐
│                    MUSIC-IO ARCHITECTURE                     │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  👁️  STAGE 1 (COM7)  →  Sensor + Botón + Servos + Brazo    │
│      - HC-SR04 Proximity Sensor (invitación)                │
│      - Botón físico (inicio de juego)                       │
│      - 2x SG90 servos (danza de inicio)                     │
│      - 1x DS04-NFC 360° servo (rotación)                    │
│      - 4x KS3518 servos (brazo robótico)                    │
│      - Relé (luces/efectos)                                 │
│                           ↓                                  │
│  🧠  ORCHESTRATOR     →  Coordinador Central (Python)       │
│      - Procesa eventos de sensores                          │
│      - Coordina secuencias robóticas                        │
│      - Gestiona flujo del juego                             │
│                           ↓                                  │
│  💨  STAGE 2 (COM4)   →  Sistema de Succión                 │
│      - Bomba de vacío                                       │
│      - Válvula solenoide                                    │
│                           ↓                                  │
│  🌐  WEB VISUALIZER   →  Interfaz de Juego                  │
│      - Juego en navegador (60 segundos)                     │
│      - WebSocket para tiempo real                           │
│      - Controles: Teclado/Joystick/Gestos                   │
│                           ↓                                  │
│  🖨️  THERMAL PRINTER  →  Recuerdo Impreso                   │
│      - ASCII art aleatorio                                  │
│      - Poema generado por IA (OpenAI)                       │
│      - Mensaje de agradecimiento                            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

### Flujo del Juego

```
1. IDLE → Usuario se acerca (< 50cm)
   ↓
2. Muestra "🎮 ¡Ven a Jugar! 🎮" en pantalla
   ↓
3. Usuario presiona botón físico
   ↓
4. Relé se activa (luces/sonidos)
   ↓
5. SG90 servos bailan por 5 segundos
   ↓
6. Juego inicia en navegador (60 segundos)
   ↓
7. Usuario juega esquivando enemigos y recolectando sushi
   ↓
8. GAME OVER:
   
   SI PUNTAJE >= 10 (VICTORIA):
   ├─→ Servo 360° baila (6 seg derecha, 3 seg izquierda)
   ├─→ Brazo robótico se extiende
   ├─→ Bomba de succión se activa (5 segundos)
   ├─→ Brazo levanta objeto
   ├─→ Brazo gira hacia jugador (75°)
   ├─→ Bomba se desactiva (suelta objeto)
   ├─→ Impresora imprime recuerdo
   └─→ Reset a IDLE
   
   SI PUNTAJE < 10 (DERROTA):
   ├─→ Relé se desactiva
   └─→ Reset a IDLE
```

## 🚀 Inicio Rápido

### Hardware Necesario

**Arduino y Sensores:**
- 2x Arduino Uno/Mega (uno para cada etapa)
- 1x HC-SR04 Sensor de Proximidad Ultrasónico
- 1x Botón físico grande
- 1x Relé (para luces/efectos)
- 1x LED (indicador)

**Servomotores:**
- 2x SG90 Servos (danza de inicio)
- 1x DS04-NFC Servo 360° (rotación continua)
- 4x KS3518 Servos (brazo robótico)
- 1x PCA9685 Controlador PWM (16 canales)

**Sistema de Succión:**
- 1x Bomba de vacío
- 1x Válvula solenoide

**Impresora:**
- 1x Impresora térmica USB (compatible con Windows)

**Otros:**
- Cables USB
- Fuente de alimentación para servos (5V, 10A recomendado)
- Webcam (opcional, para control por gestos)

### Software Necesario

- Python 3.11+
- Arduino IDE
- Navegador web moderno (Chrome/Firefox/Edge)

### Instalación

**1. Clonar el repositorio:**
```bash
git clone https://github.com/tu-usuario/Music-IO.git
cd Music-IO
```

**2. Instalar dependencias de Python:**
```bash
pip install -r requirements.txt
```

**3. Configurar Arduino Stage 1 (COM7):**
- Abrir `arduino/servo_controller/stage_1.ino` en Arduino IDE
- Conectar Arduino a COM7
- Subir el código
- **Conexiones:**
  - HC-SR04: TRIG→Pin7, ECHO→Pin6
  - Botón: Pin9 (con pull-up interno)
  - Relé: Pin8
  - LED: Pin10
  - PCA9685: SDA→A4, SCL→A5

**4. Configurar Arduino Stage 2 (COM4):**
- Abrir `arduino/servo_controller/stage_2.ino` en Arduino IDE
- Conectar Arduino a COM4
- Subir el código
- **Conexiones:**
  - Bomba de vacío: Pin controlado por relé
  - Válvula solenoide: Pin controlado por relé

**5. Configurar Impresora Térmica:**
- Conectar impresora USB
- Instalar drivers si es necesario
- El sistema auto-detectará la impresora

**6. (Opcional) Configurar OpenAI para poemas:**
- Crear archivo `config.properties` en la raíz:
```properties
OPENAI_API_KEY=tu_api_key_aqui
OPENAI_MODEL=gpt-4o-mini
```

**7. Ejecutar el sistema completo:**
```bash
python run_with_visualizer.py
```

**8. Abrir el juego en el navegador:**
```
http://127.0.0.1:5000/game
```

### Uso

**Modo Jugador:**
1. Acércate a la máquina (< 50cm)
2. Verás "🎮 ¡Ven a Jugar! 🎮" en pantalla
3. Presiona el botón físico grande
4. Disfruta la danza de los servos (5 segundos)
5. Juega en el navegador:
   - **Teclado**: Flechas para moverte, Espacio para saltar
   - **Joystick USB**: Conectar y jugar
   - **Gestos**: Levanta manos para controlar dificultad
6. Sobrevive 60 segundos y consigue 10+ puntos
7. ¡Recibe tu premio del brazo robótico!
8. Obtén tu recuerdo impreso

**Controles del Juego:**
- ⬅️➡️ Flechas: Mover personaje
- ⬆️ Flecha arriba: Saltar
- 🎮 Joystick: Soporte completo
- 👋 Mano izquierda arriba: Aparece enemigo
- 👋 Mano derecha arriba: Aparece sushi (puntos)

## 📁 Estructura del Proyecto

```
Music-IO/
├── src/
│   ├── core/                           # Dominio Central (Lógica de Negocio)
│   │   ├── domain/
│   │   │   ├── events.py               # Eventos del dominio
│   │   │   ├── state_machine.py        # Máquina de estados
│   │   │   └── orchestrator.py         # ⭐ Orquestador de sonidos
│   │   └── ports/                      # Interfaces (contratos)
│   │       ├── input_port.py           # Puerto de entrada
│   │       └── output_port.py          # Puerto de salida
│   │
│   ├── adapters/                       # Implementaciones
│   │   ├── input/
│   │   │   ├── arduino_adapter.py      # Sensor de proximidad (opcional)
│   │   │   └── button_adapter.py       # Botón físico
│   │   └── output/
│   │       ├── local_audio_adapter.py  # Audio local
│   │       ├── servo_adapter.py        # ⭐ Stage 1 (COM7)
│   │       ├── pump_adapter.py         # ⭐ Stage 2 (COM4)
│   │       ├── thermal_printer_adapter_win.py  # ⭐ Impresora
│   │       └── web_visualizer_adapter.py       # ⭐ Visualizador web
│   │
│   └── app/                            # Capa de Aplicación
│       ├── application.py              # ⭐ Conecta todo el sistema
│       └── main.py                     # Punto de entrada
│
├── arduino/                            # Código Arduino
│   ├── servo_controller/
│   │   ├── stage_1.ino                 # ⭐ Stage 1 (COM7) - Principal
│   │   └── stage_2.ino                 # ⭐ Stage 2 (COM4) - Bomba
│   ├── proximity_sensor/               # Sensor standalone (opcional)
│   ├── button_controller/              # Botón standalone (opcional)
│   └── README.md
│
├── web/
│   └── templates/
│       └── game_visualizer.html        # ⭐ Juego web completo
│
├── docs/                               # Documentación
│   ├── ORCHESTRATOR.md                 # Arquitectura del orquestador
│   ├── PULSE_JUMP_GAME.md             # Documentación del juego
│   └── WEB_VISUALIZER.md              # Visualizador web
│
├── payment/                            # Sistema de pagos (Solana)
│   └── smart_contract/                 # Contrato inteligente
│
├── run_with_visualizer.py              # ⭐ Script principal de ejecución
├── requirements.txt                    # Dependencias Python
├── config.properties                   # Configuración (API keys)
├── COMO_FUNCIONA.md                    # ⭐ Guía completa en español
└── README.md                           # Este archivo
```

## 🏗️ Arquitectura Hexagonal

### Principios de Diseño

**1. Núcleo del Dominio (Centro)**
   - `SoundOrchestrator`: Coordina múltiples sonidos simultáneos
   - `MusicStateMachine`: Máquina de estados para lógica del juego
   - Eventos del dominio: `ProximityEvent`, `SoundEvent`, `ButtonEvent`
   - Sin dependencias externas

**2. Puertos (Interfaces)**
   - `InputPort`: Contrato para todas las fuentes de entrada
   - `OutputPort`: Contrato para todos los destinos de salida
   - Permite intercambiar implementaciones sin cambiar el núcleo

**3. Adaptadores (Implementaciones)**
   - **Entrada**: `ButtonAdapter`, `ArduinoAdapter` (proximidad)
   - **Salida**: `ServoAdapter` (Stage 1), `PumpAdapter` (Stage 2), `ThermalPrinterAdapter`, `WebVisualizerAdapter`, `LocalAudioAdapter`
   - Cada adaptador es independiente y reemplazable

### Sistema de 2 Etapas

**Stage 1 (COM7) - Controlador Principal:**
- Sensor de proximidad HC-SR04
- Botón físico de inicio
- 2x SG90 servos (danza)
- 1x DS04-NFC servo 360° (rotación)
- 4x KS3518 servos (brazo robótico)
- Relé para efectos
- Coordina con Python para control de bomba

**Stage 2 (COM4) - Controlador de Bomba:**
- Bomba de succión
- Válvula solenoide
- Recibe comandos de Python vía serial
- Activación/desactivación sincronizada con brazo

### Beneficios

- ✅ **Modularidad**: Cada componente es independiente
- ✅ **Testabilidad**: Probar cada parte por separado
- ✅ **Escalabilidad**: Agregar nuevos juegos o hardware fácilmente
- ✅ **Mantenibilidad**: Código organizado y documentado
- ✅ **Extensibilidad**: Arquitectura preparada para crecer

## 🎮 Cómo Funciona

### Máquina de Estados

```
IDLE → GAME_STARTED → WAITING_FOR_RESULT → WIN_SEQUENCE → IDLE
```

**1. IDLE (Esperando)**
   - Sensor de proximidad activo
   - Muestra invitación si usuario < 50cm
   - Espera presión de botón

**2. GAME_STARTED (Juego Iniciado)**
   - Relé se activa (luces/sonidos)
   - SG90 servos bailan 5 segundos
   - Juego web se inicia

**3. WAITING_FOR_RESULT (Esperando Resultado)**
   - Usuario juega 60 segundos
   - Sistema espera señal WIN o LOSE

**4. WIN_SEQUENCE (Secuencia de Victoria)** - Solo si puntaje >= 10
   - Servo 360° baila (6s derecha + 3s izquierda)
   - Brazo robótico se extiende en 11 pasos:
     1. Brazos inferiores adelante (90°)
     2. Brazo superior alineado (90°)
     3. Brazos a posición de agarre
     4. Antebrazo adelante 35°
     5. Antebrazo abajo 20°
     6. Brazo izquierdo abajo 45°
     7. Base gira 30° izquierda
     8. Brazo izquierdo abajo 90° + **BOMBA ON** (5 seg)
     9. Antebrazo regresa + **BOMBA OFF**
     10. Base gira 75° izquierda (entrega)
     11. Colapso a posición inicial
   - Impresora imprime recuerdo
   - Reset a IDLE

**5. LOSE (Derrota)** - Si puntaje < 10
   - Relé se desactiva
   - Reset directo a IDLE

### Comunicación Serial

**Python → Stage 1 (COM7):**
- `"WIN"` - Ejecutar secuencia de victoria
- `"LOSE"` - Resetear a idle
- `"START_GAME"` - Iniciar desde web
- `"RESET"` - Resetear sistema

**Stage 1 → Python:**
- `{"button":"pressed"}` - Botón presionado
- `{"invite":"Ven a Jugar"}` - Mostrar invitación
- `{"invite":""}` - Ocultar invitación
- `{"action":"activate_pump"}` - Activar bomba (Stage 2)
- `{"action":"deactivate_pump"}` - Desactivar bomba
- `{"status":"..."}` - Estados de secuencia

**Python → Stage 2 (COM4):**
- `"PUMP_ON"` - Activar bomba de succión
- `"PUMP_OFF"` - Desactivar bomba

## 🔧 Configuración

### Puertos COM

Editar `run_with_visualizer.py` si tus Arduinos están en puertos diferentes:

```python
app = MusicMachineApplication(
    enable_visualizer=True,
    enable_button=True,
    enable_servo=True,    # Stage 1 - Cambiar puerto en servo_adapter.py
    enable_pump=True,     # Stage 2 - Cambiar puerto en pump_adapter.py
    enable_printer=True
)
```

**Puertos por defecto:**
- Stage 1 (Servo): `COM7`
- Stage 2 (Pump): `COM4`

### Impresora Térmica

El sistema auto-detecta impresoras USB. Para especificar manualmente:

```python
app = MusicMachineApplication(
    enable_printer=True,
    printer_port="Generic / Text Only"  # Nombre de impresora Windows
)
```

### OpenAI (Poemas)

Crear `config.properties` en la raíz:

```properties
OPENAI_API_KEY=sk-tu-api-key-aqui
OPENAI_MODEL=gpt-4o-mini
```

Sin API key, el sistema funciona pero no genera poemas.

### Ajustes del Juego

Editar `web/templates/game_visualizer.html`:

```javascript
const GAME_DURATION = 60;  // Duración en segundos
const WIN_THRESHOLD = 10;  // Puntos mínimos para ganar
```

## 🧪 Testing y Diagnóstico

### Test de Componentes Individuales

**Test del Botón:**
```bash
python simple_button_test.py
```

**Test del Servo (Stage 1):**
```bash
python test_servo.py
```

**Test de la Bomba (Stage 2):**
```bash
python test_pump.py
```

**Test de Impresora:**
```bash
python test_thermal_printer.py
```

**Diagnóstico de Puertos:**
```bash
python check_ports.py
```

### Monitor Serial Arduino

**Stage 1 (COM7):**
1. Abrir Arduino Serial Monitor
2. Baudrate: 9600
3. Deberías ver:
   - `{"status":"ready"}`
   - `{"invite":"Ven a Jugar"}` (cuando te acercas)
   - `{"button":"pressed"}` (al presionar)

**Stage 2 (COM4):**
1. Abrir Arduino Serial Monitor
2. Baudrate: 9600
3. Enviar comandos:
   - `PUMP_ON` → Activa bomba
   - `PUMP_OFF` → Desactiva bomba

## 🔌 Extensibilidad

### Agregar Nuevos Juegos

1. Crear nuevo HTML en `web/templates/`
2. Implementar lógica del juego en JavaScript
3. Usar WebSocket para comunicación:
   ```javascript
   socket.emit('game_over', {score: finalScore});
   ```
4. El sistema manejará automáticamente WIN/LOSE

### Agregar Nuevos Sensores

1. Crear adaptador en `src/adapters/input/`
2. Implementar interfaz `InputPort`
3. Registrar en `application.py`:
   ```python
   self.new_sensor = NewSensorAdapter()
   self.new_sensor.register_callback(self._handle_sensor_event)
   ```

### Agregar Nuevos Actuadores

1. Crear adaptador en `src/adapters/output/`
2. Implementar interfaz `OutputPort`
3. Integrar en secuencias del orquestador

### Sistema de Pagos (Blockchain)

El proyecto incluye integración con Solana:
- Contrato inteligente en `payment/smart_contract/`
- Generación de QR codes para pagos
- Ver `payment/README.md` para detalles

## 📝 Logs y Monitoreo

**Logs del Sistema:**
- Console (stdout) - Eventos en tiempo real
- Logs de Python en consola
- Logs de Arduino en Serial Monitor

**Niveles de Log:**
- `INFO`: Operación general
- `DEBUG`: Eventos detallados
- `WARNING`: Advertencias
- `ERROR`: Errores

**Monitoreo en Tiempo Real:**
- Dashboard web: `http://127.0.0.1:5000`
- WebSocket para actualizaciones instantáneas
- Estado del orquestador visible en consola

## 🐛 Solución de Problemas

### Arduino No Detectado

**Problema:** `Failed to initialize servo controller on COM7`

**Soluciones:**
1. Verificar conexión USB
2. Instalar drivers CH340/CH341 (para clones)
3. Verificar puerto en Administrador de Dispositivos (Windows)
4. Ejecutar `python check_ports.py` para ver puertos disponibles
5. Cerrar Arduino IDE (puede bloquear el puerto)

### Bomba No Responde

**Problema:** Bomba no se activa en secuencia de victoria

**Soluciones:**
1. Verificar que Stage 2 está en COM4
2. Probar con `python test_pump.py`
3. Verificar alimentación de la bomba (5V, suficiente amperaje)
4. Revisar conexiones del relé

### Impresora No Imprime

**Problema:** `Failed to initialize thermal printer`

**Soluciones:**
1. Verificar que la impresora está conectada por USB
2. Instalar drivers de la impresora
3. Verificar en "Dispositivos e impresoras" de Windows
4. Probar con `python test_thermal_printer.py`
5. El sistema funciona sin impresora (característica opcional)

### Juego No Inicia en Navegador

**Problema:** Página no carga o no responde

**Soluciones:**
1. Verificar que `run_with_visualizer.py` está ejecutándose
2. Abrir `http://127.0.0.1:5000/game` (no localhost)
3. Verificar firewall de Windows
4. Revisar consola de Python para errores
5. Probar en modo incógnito del navegador

### Servos No Se Mueven

**Problema:** Servos no responden o se mueven erráticamente

**Soluciones:**
1. Verificar alimentación (5V, 10A recomendado para todos los servos)
2. Verificar conexiones del PCA9685
3. Probar con `python test_servo.py`
4. Revisar que I2C está correctamente conectado (SDA→A4, SCL→A5)
5. Verificar que no hay cortocircuitos

### PyAudio/PyWin32 No Instala

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
pip install pywin32
```

**Si persiste:**
```bash
pip install --upgrade pip
pip install pyaudio --user
```

### Ver Documentación Completa

Para más detalles, consultar:
- `TROUBLESHOOTING.md` - Guía completa de problemas
- `COMO_FUNCIONA.md` - Explicación detallada del sistema
- `ARDUINO_SETUP.md` - Configuración de hardware

## 📚 Documentación Adicional

### Guías Principales
- **`COMO_FUNCIONA.md`** - Explicación completa para todos los niveles
- **`QUICKSTART.md`** - Inicio rápido en 5 minutos
- **`ARCHITECTURE.md`** - Arquitectura técnica detallada
- **`TROUBLESHOOTING.md`** - Solución de problemas

### Documentación Técnica
- **`docs/ORCHESTRATOR.md`** - Sistema de orquestación
- **`docs/PULSE_JUMP_GAME.md`** - Documentación del juego
- **`docs/WEB_VISUALIZER.md`** - Visualizador web
- **`ARDUINO_SETUP.md`** - Configuración de hardware
- **`BUTTON_TEST_GUIDE.md`** - Testing de botón
- **`BUTTON_SERVO_TEST_GUIDE.md`** - Testing de servos

### Referencias Externas
- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Arduino PCA9685 Library](https://github.com/adafruit/Adafruit-PWM-Servo-Driver-Library)
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/)

## 🤝 Contribuir

Music-IO es **open source** y acepta contribuciones:

**Sin programar:**
- 🎨 Diseño visual y gráficos
- 🎵 Efectos de sonido y música
- 📝 Documentación y traducciones
- 🎮 Diseño de nuevos juegos
- 🧪 Testing y reporte de bugs

**Programando:**
- 🎮 Nuevos juegos web
- 🤖 Mejoras al brazo robótico
- 🔌 Nuevos sensores y actuadores
- 🌐 Funciones web (leaderboards, social)
- 💰 Sistema de pagos mejorado

**Cómo contribuir:**
1. Fork del repositorio
2. Crear branch para tu feature
3. Hacer tus cambios
4. Probar que funciona
5. Crear Pull Request

## 📄 Licencia

MIT License - Libre para usar y modificar

## 🎯 Roadmap

### Completado ✅
- [x] Sistema de 2 etapas (Stage 1 y Stage 2)
- [x] Brazo robótico con 11 pasos
- [x] Sistema de succión sincronizado
- [x] Impresora térmica con ASCII art y poemas IA
- [x] Juego web con controles múltiples
- [x] Sensor de proximidad con invitación
- [x] Arquitectura hexagonal completa
- [x] WebSocket para tiempo real
- [x] Integración con Solana blockchain

### En Progreso 🚧
- [ ] Sistema de leaderboards online
- [ ] Múltiples juegos seleccionables
- [ ] App móvil para control remoto
- [ ] Sistema de logros y trofeos

### Futuro 🔮
- [ ] Reconocimiento facial para jugadores recurrentes
- [ ] Integración con redes sociales
- [ ] Modo multijugador
- [ ] Versión portátil con batería
- [ ] Kit comercial para venta
- [ ] Versión educativa para escuelas

## 🌟 Créditos

**Desarrollado con:**
- Python + Flask + SocketIO
- Arduino + PCA9685
- HTML5 Canvas + JavaScript
- OpenAI API
- Solana Blockchain

**Agradecimientos:**
- Comunidad open source
- Todos los contribuidores
- Jugadores y testers

---

**🎮 Construido con ❤️ usando Arquitectura Hexagonal**

**¿Preguntas? ¿Ideas? ¿Quieres construir tu propia Music-IO?**

Abre un Issue en GitHub o consulta `COMO_FUNCIONA.md` para una guía completa.

*Última actualización: Enero 2026*
