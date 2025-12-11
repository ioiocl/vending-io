# Sound Orchestrator Documentation

## Overview

The **Sound Orchestrator** is the conductor of the Music-IO system. It coordinates multiple sound sources, manages simultaneous sounds, and applies musical rules and patterns.

## Architecture Position

```
┌─────────────────────────────────────────────────────────┐
│                    CORE DOMAIN                          │
│                                                         │
│  ┌──────────────┐         ┌──────────────┐            │
│  │ State Machine│         │ Orchestrator │ ◀── YOU ARE HERE
│  │ (Individual) │────────▶│ (Coordinator)│            │
│  └──────────────┘         └──────────────┘            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

The orchestrator sits in the **CORE DOMAIN** because:
- It contains business logic (how to coordinate sounds)
- It's independent of technology (doesn't know about Arduino or PyAudio)
- It's testable without hardware
- It coordinates multiple state machines

## Key Features

### 1. Multiple Simultaneous Sounds 🎵

The orchestrator can manage up to 8 sounds playing at the same time:

```python
orchestrator = SoundOrchestrator(max_simultaneous_sounds=8)

# Add multiple sounds
orchestrator.add_sound(sound1, "track1", priority=5)
orchestrator.add_sound(sound2, "track2", priority=3)
orchestrator.add_sound(sound3, "track3", priority=7)

# Get all active sounds for mixing
sounds = orchestrator.get_active_sounds()  # Returns [sound1, sound2, sound3]
```

### 2. Multiple Input Sources 🎹

Each input source gets its own state machine:

```python
# Register different input sources
orchestrator.register_input_source("arduino_proximity")
orchestrator.register_input_source("midi_controller")
orchestrator.register_input_source("web_api")

# Process events from different sources
orchestrator.process_proximity_event(event1, source_id="arduino_proximity")
orchestrator.process_proximity_event(event2, source_id="midi_controller")
```

### 3. Priority System 🎯

Sounds have priorities. If at capacity, lower priority sounds are removed:

```python
# High priority sound (will stay)
orchestrator.add_sound(important_sound, "alert", priority=10)

# Low priority sound (may be removed if capacity reached)
orchestrator.add_sound(background_sound, "ambient", priority=1)
```

### 4. Mix Modes 🎚️

Three mixing strategies:

#### Additive Mode (Default)
All sounds play together, mixed additively:
```python
orchestrator.set_mix_mode("additive")
# Result: All sounds play at full volume
```

#### Priority Mode
Only the highest priority sound plays:
```python
orchestrator.set_mix_mode("priority")
# Result: Only the most important sound plays
```

#### Layered Mode
All sounds play with reduced volume to prevent clipping:
```python
orchestrator.set_mix_mode("layered")
# Result: Each sound's volume is divided by the number of active sounds
```

### 5. Automatic Cleanup 🧹

Expired sounds are automatically removed:

```python
# Sound plays for 0.5 seconds
sound = SoundEvent(frequency=440, duration=0.5, amplitude=0.5)
orchestrator.add_sound(sound, "temp", priority=5)

# After 0.5 seconds, automatically removed
# orchestrator._cleanup_expired_tracks() is called automatically
```

### 6. Harmony Generation 🎼

Generate harmonic sounds based on a base frequency:

```python
# Generate major triad (root, major third, perfect fifth)
harmonics = orchestrator.apply_harmony(440.0)  # A4 note

# Result:
# - 440 Hz (root)
# - 550 Hz (major third)
# - 660 Hz (perfect fifth)
```

## Usage Examples

### Example 1: Single Sensor

```python
# Initialize
orchestrator = SoundOrchestrator(max_simultaneous_sounds=8)

# Process proximity event
proximity_event = ProximityEvent(distance=15.0)
sounds = orchestrator.process_proximity_event(
    proximity_event,
    source_id="arduino_proximity"
)

# Play all sounds
for sound in sounds:
    audio_adapter.play_sound(sound)
```

### Example 2: Multiple Sensors

```python
# Two proximity sensors
sensor1_event = ProximityEvent(distance=10.0, sensor_id="sensor1")
sensor2_event = ProximityEvent(distance=30.0, sensor_id="sensor2")

# Process both
sounds1 = orchestrator.process_proximity_event(sensor1_event, "sensor1")
sounds2 = orchestrator.process_proximity_event(sensor2_event, "sensor2")

# Both sounds play simultaneously
```

### Example 3: With Harmony

```python
# Process proximity
proximity_event = ProximityEvent(distance=15.0)
sounds = orchestrator.process_proximity_event(proximity_event, "arduino")

# Add harmony
if sounds:
    base_frequency = sounds[0].frequency
    orchestrator.apply_harmony(base_frequency)

# Now plays: base note + harmony (4 sounds total)
```

### Example 4: Priority Management

```python
# Background ambient sound (low priority)
ambient = SoundEvent(frequency=200, duration=5.0, amplitude=0.2)
orchestrator.add_sound(ambient, "ambient", priority=1)

# Alert sound (high priority)
alert = SoundEvent(frequency=1000, duration=0.5, amplitude=0.8)
orchestrator.add_sound(alert, "alert", priority=10)

# If at capacity, ambient will be removed to make room for alert
```

## Status Monitoring

Get detailed orchestrator status:

```python
status = orchestrator.get_status()

# Returns:
{
    "active_tracks": 3,
    "max_tracks": 8,
    "mix_mode": "additive",
    "tempo_bpm": None,
    "master_volume": 1.0,
    "input_sources": ["arduino_proximity", "midi_controller"],
    "tracks": [
        {
            "track_id": "arduino_proximity_1234567890.123",
            "frequency": 700,
            "priority": 5,
            "source": "arduino_proximity",
            "age_seconds": 0.15
        },
        # ... more tracks
    ]
}
```

## Integration with Application

The orchestrator is integrated in `application.py`:

```python
class MusicMachineApplication:
    def __init__(self):
        # Create orchestrator instead of state machine
        self.orchestrator = SoundOrchestrator(max_simultaneous_sounds=8)
    
    def _handle_input_event(self, proximity_event):
        # Orchestrator processes and returns multiple sounds
        sound_events = self.orchestrator.process_proximity_event(
            proximity_event,
            source_id="arduino_proximity"
        )
        
        # Play all orchestrated sounds
        for sound_event in sound_events:
            self._play_sound(sound_event)
```

## Data Flow with Orchestrator

```
Arduino Sensor (15cm)
    ↓
ProximityEvent(distance=15.0)
    ↓
┌─────────────────────────────────────┐
│      ORCHESTRATOR (CORE)            │
│                                     │
│  1. Get/Create State Machine        │
│     for "arduino_proximity"         │
│                                     │
│  2. State Machine processes:        │
│     15cm → 700 Hz                   │
│                                     │
│  3. Add to active tracks:           │
│     track_id: "arduino_proximity_..." │
│     priority: 5                     │
│                                     │
│  4. Cleanup expired tracks          │
│                                     │
│  5. Return all active sounds        │
│     (may be multiple)               │
└─────────────────────────────────────┘
    ↓
[SoundEvent(700Hz), SoundEvent(440Hz), ...]
    ↓
Audio Adapter (plays all)
    ↓
Speakers (mixed sound)
```

## Future Enhancements

### Tempo Synchronization
```python
orchestrator.set_tempo(120)  # 120 BPM
# All sounds align to tempo grid
```

### Pattern Engine
```python
orchestrator.apply_pattern("arpeggio")
# Plays notes in sequence: C → E → G → C
```

### Effects Chain
```python
orchestrator.add_effect("reverb", amount=0.3)
orchestrator.add_effect("delay", time=0.5)
```

### MIDI Integration
```python
orchestrator.register_input_source("midi")
midi_event = MIDIEvent(note=60, velocity=100)
orchestrator.process_midi_event(midi_event, "midi")
```

## Benefits

1. **Scalability**: Easy to add more input sources
2. **Flexibility**: Different mixing strategies
3. **Coordination**: Manages multiple sounds intelligently
4. **Clean Architecture**: Stays in core domain
5. **Testability**: Can test without hardware

## Testing

```python
# Unit test without hardware
def test_orchestrator():
    orch = SoundOrchestrator(max_simultaneous_sounds=2)
    
    # Add sounds
    sound1 = SoundEvent(440, 0.5, 0.5)
    sound2 = SoundEvent(550, 0.5, 0.5)
    sound3 = SoundEvent(660, 0.5, 0.5)
    
    orch.add_sound(sound1, "s1", priority=5)
    orch.add_sound(sound2, "s2", priority=3)
    
    # At capacity (2 sounds)
    assert len(orch.active_tracks) == 2
    
    # Add higher priority sound
    orch.add_sound(sound3, "s3", priority=7)
    
    # Lower priority sound removed
    assert len(orch.active_tracks) == 2
    assert "s2" not in orch.active_tracks
    assert "s3" in orch.active_tracks
```

---

**The orchestrator is the conductor of your music machine!** 🎼
