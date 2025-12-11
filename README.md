# Music-IO

**Hexagonal Architecture Music Machine** - An extensible system that converts sensor input into sound using clean architecture principles.

## 🎵 Overview

Music-IO is a music generation system built with **hexagonal architecture** (ports and adapters pattern). It uses a **state machine orchestrator** in the core to process sensor inputs and generate sound outputs.

### Current Features

- **Input**: Arduino proximity sensor (HC-SR04)
- **Output**: Local audio playback
- **Core**: State machine that converts distance to musical frequencies

### Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    HEXAGONAL ARCHITECTURE                │
├─────────────────────────────────────────────────────────┤
│                                                          │
│  ┌──────────────┐         ┌──────────────┐             │
│  │   Arduino    │────────▶│  Input Port  │             │
│  │   Adapter    │         │  (Interface) │             │
│  └──────────────┘         └──────┬───────┘             │
│                                   │                      │
│                                   ▼                      │
│                          ┌─────────────────┐            │
│                          │   CORE DOMAIN   │            │
│                          │                 │            │
│                          │  State Machine  │            │
│                          │   Orchestrator  │            │
│                          │                 │            │
│                          │  Business Logic │            │
│                          └─────────┬───────┘            │
│                                    │                     │
│                                    ▼                     │
│  ┌──────────────┐         ┌──────────────┐             │
│  │ Local Audio  │◀────────│ Output Port  │             │
│  │   Adapter    │         │  (Interface) │             │
│  └──────────────┘         └──────────────┘             │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

### Future Extensibility

The architecture is designed to easily add:

**Input Adapters:**
- More sensors (temperature, light, motion)
- Human interaction (MIDI controllers, keyboards)
- Blockchain events (on-chain data)
- Web APIs
- OSC (Open Sound Control)

**Output Adapters:**
- Ableton Live integration
- SuperCollider
- Visual servers (Processing, TouchDesigner)
- MIDI output
- Network streaming

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Arduino board (Uno, Nano, Mega)
- HC-SR04 Ultrasonic Proximity Sensor
- USB cable

### Installation

1. **Clone or download this repository**

2. **Install Python dependencies:**
```bash
pip install -r requirements.txt
```

3. **Set up Arduino:**
   - Follow instructions in `arduino/README.md`
   - Upload `arduino/proximity_sensor/proximity_sensor.ino` to your Arduino
   - Connect HC-SR04 sensor (see wiring diagram in arduino/README.md)

4. **Run the application:**
```bash
cd src
python -m app.main
```

### Usage

1. Start the application
2. Move your hand near the proximity sensor
3. Hear the sound change based on distance:
   - **Close (0-10cm)**: High frequency (800-1200 Hz)
   - **Medium (10-30cm)**: Mid frequency (400-800 Hz)
   - **Far (30-50cm)**: Low frequency (200-400 Hz)

## 📁 Project Structure

```
Music-IO/
├── src/
│   ├── core/                    # Core Domain (Business Logic)
│   │   ├── domain/
│   │   │   ├── events.py        # Domain events
│   │   │   └── state_machine.py # State machine orchestrator
│   │   └── ports/               # Interfaces (contracts)
│   │       ├── input_port.py
│   │       └── output_port.py
│   │
│   ├── adapters/                # Implementations
│   │   ├── input/
│   │   │   └── arduino_adapter.py
│   │   └── output/
│   │       └── local_audio_adapter.py
│   │
│   └── app/                     # Application Layer
│       ├── application.py       # Wires everything together
│       └── main.py             # Entry point
│
├── arduino/                     # Arduino code
│   ├── proximity_sensor/
│   │   └── proximity_sensor.ino
│   └── README.md
│
├── requirements.txt
└── README.md
```

## 🏗️ Architecture Principles

### Hexagonal Architecture (Ports & Adapters)

1. **Core Domain** (Center)
   - Contains business logic
   - State machine orchestrator
   - Domain events
   - No dependencies on external frameworks

2. **Ports** (Interfaces)
   - Define contracts
   - `InputPort`: Interface for all input sources
   - `OutputPort`: Interface for all output destinations

3. **Adapters** (Implementations)
   - Implement port interfaces
   - Connect to external systems
   - Can be swapped without changing core logic

### Benefits

- **Testability**: Core logic can be tested independently
- **Flexibility**: Easy to swap adapters (e.g., replace Arduino with web API)
- **Maintainability**: Clear separation of concerns
- **Extensibility**: Add new inputs/outputs without modifying core

## 🎼 How It Works

### State Machine Flow

```
IDLE → LISTENING → PROCESSING → PLAYING → LISTENING
```

1. **IDLE**: Waiting for input
2. **LISTENING**: Proximity detected
3. **PROCESSING**: Converting distance to sound parameters
4. **PLAYING**: Sound is being generated
5. Back to **LISTENING** for next input

### Distance to Sound Mapping

The core business logic maps proximity to musical parameters:

```python
Distance (cm)  →  Frequency (Hz)  →  Amplitude
0-10          →  1200-800        →  0.8 (loud)
10-30         →  800-400         →  0.6 (medium)
30-50         →  400-200         →  0.4 (quiet)
>50           →  No sound        →  0.0
```

## 🔧 Configuration

### Arduino Settings

Edit `src/adapters/input/arduino_adapter.py`:
```python
ArduinoAdapter(
    port="COM3",        # Your serial port
    baud_rate=9600,     # Must match Arduino
    auto_detect=True    # Auto-find Arduino
)
```

### Audio Settings

Edit `src/adapters/output/local_audio_adapter.py`:
```python
LocalAudioAdapter(
    sample_rate=44100,  # Audio quality
    channels=1          # 1=mono, 2=stereo
)
```

## 🧪 Testing

### Test Audio Output
```python
from src.app.application import MusicMachineApplication

app = MusicMachineApplication()
app.output_adapter.initialize()
app.test_audio()  # Plays 440Hz tone
```

### Test Arduino Connection
1. Open Arduino Serial Monitor
2. Set baud rate to 9600
3. Should see: `{"distance": XX.X}`

## 🚧 Adding New Adapters

### Adding a New Input Adapter

1. Create new adapter in `src/adapters/input/`
2. Implement `InputPort` interface
3. Register callback for events
4. Inject into application

Example:
```python
class WebAPIAdapter(InputPort):
    def start(self): ...
    def stop(self): ...
    def register_callback(self, callback): ...
```

### Adding a New Output Adapter

1. Create new adapter in `src/adapters/output/`
2. Implement `OutputPort` interface
3. Handle `SoundEvent` objects
4. Inject into application

Example:
```python
class AbletonAdapter(OutputPort):
    def initialize(self): ...
    def play_sound(self, sound_event): ...
    def stop(self): ...
```

## 📝 Logging

Logs are written to:
- Console (stdout)
- `music_machine.log` file

Log levels:
- `INFO`: General operation
- `DEBUG`: Detailed events
- `ERROR`: Problems

## 🐛 Troubleshooting

### Arduino Not Found
- Check USB connection
- Install CH340 drivers (for clone boards)
- Manually specify port: `ArduinoAdapter(port="COM3")`

### No Audio Output
- Check system audio settings
- Try different sample rate
- Install PyAudio dependencies (see platform-specific notes)

### PyAudio Installation Issues

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

**Linux:**
```bash
sudo apt-get install portaudio19-dev python3-pyaudio
pip install pyaudio
```

**macOS:**
```bash
brew install portaudio
pip install pyaudio
```

## 📚 Further Reading

- [Hexagonal Architecture](https://alistair.cockburn.us/hexagonal-architecture/)
- [Ports and Adapters Pattern](https://herbertograca.com/2017/09/14/ports-adapters-architecture/)
- [State Machine Pattern](https://refactoring.guru/design-patterns/state)

## 🤝 Contributing

This is a starting point for an extensible music system. Feel free to:
- Add new input adapters
- Add new output adapters
- Enhance the state machine logic
- Improve the sound generation algorithms

## 📄 License

MIT License - Feel free to use and modify

## 🎯 Roadmap

- [ ] Add MIDI input adapter
- [ ] Add Ableton Live output adapter
- [ ] Add SuperCollider output adapter
- [ ] Add visual output (Processing/TouchDesigner)
- [ ] Add blockchain event input adapter
- [ ] Add web API input adapter
- [ ] Add configuration file support
- [ ] Add GUI for monitoring
- [ ] Add recording/playback functionality
- [ ] Add multiple simultaneous inputs
- [ ] Add audio effects processing

---

**Built with ❤️ using Hexagonal Architecture**
