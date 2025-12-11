# Arduino Controllers Setup

## Stage Controllers

### Stage 1 - Main Robotic Sequence (COM7)
**File:** `servo_controller/stage_1.ino`

Controls the main robotic sequence:
1. **Button press** → SG90 dance (game initiation)
2. **Wait for WIN/LOSE** signal from Python
3. **On WIN:** DS04 360° sequence → Arm pick-down → Signal pump → Arm lift
4. **Reset** and wait for next button press

**Hardware:**
- PCA9685 PWM Driver
- 2x SG90 Servos (pins 0, 1)
- DS04-NFC 360° Servo (pin 3)
- KS3518 Robotic Arm Servos (pins 8-11)
- Button on pin 9

### Stage 2 - Pump Controller (COM4)
**File:** `servo_controller/stage_2.ino`

Receives pump activation/deactivation signals via serial from Python:
- `ACTIVATE_PUMP` - Opens valve, turns on suction
- `DEACTIVATE_PUMP` - Turns off pump, closes valve
- `RESET` - Returns to initial state

**Hardware:**
- Servo-controlled pump on pin 9
- Servo-controlled valve on pin 10

---

# Arduino Proximity Sensor Setup

## Hardware Requirements

- **Arduino Board** (Uno, Nano, Mega, or compatible)
- **HC-SR04 Ultrasonic Proximity Sensor**
- **USB Cable** (for connecting Arduino to computer)
- **Jumper Wires**

## Wiring Diagram

Connect the HC-SR04 sensor to your Arduino as follows:

```
HC-SR04          Arduino
--------         -------
VCC      -----> 5V
GND      -----> GND
TRIG     -----> Pin 9
ECHO     -----> Pin 10
```

## Software Setup

### 1. Install Arduino IDE

Download and install the Arduino IDE from: https://www.arduino.cc/en/software

### 2. Upload the Code

1. Open Arduino IDE
2. Open the file `proximity_sensor.ino`
3. Select your Arduino board: **Tools > Board > Arduino Uno** (or your board model)
4. Select the correct port: **Tools > Port > COM3** (or your port)
5. Click the **Upload** button (→)

### 3. Verify Operation

1. Open the Serial Monitor: **Tools > Serial Monitor**
2. Set baud rate to **9600**
3. You should see JSON messages like: `{"distance": 25.5}`
4. Move your hand in front of the sensor to see distance changes

## How It Works

The HC-SR04 sensor works by:
1. Sending an ultrasonic pulse (40 kHz)
2. Measuring the time it takes for the echo to return
3. Calculating distance: `distance = (time × speed_of_sound) / 2`

**Range**: 2cm to 400cm  
**Accuracy**: ±3mm  
**Measurement Interval**: 50ms (20 readings per second)

## Data Format

The Arduino sends distance measurements as JSON:

```json
{"distance": 25.5}
```

Where distance is in centimeters with one decimal place.

## Troubleshooting

### No Serial Port Found
- Make sure Arduino is connected via USB
- Install CH340 drivers if using a clone board
- Try a different USB cable

### Erratic Readings
- Check wiring connections
- Ensure sensor is not too close to objects (min 2cm)
- Avoid soft materials that absorb sound (fabric, foam)
- Keep sensor away from other ultrasonic sources

### No Data Received
- Check baud rate is set to 9600
- Verify correct COM port is selected
- Press the reset button on Arduino
- Re-upload the code

## Commands

You can send commands to the Arduino via serial:

- `ping` - Test communication
- `status` - Get sensor status
- `test` - Blink LED 5 times

## Future Enhancements

This code is designed to be extensible. Future additions could include:

- Multiple sensors
- Calibration commands
- Adjustable measurement intervals
- Different output formats
- Sensor health monitoring
