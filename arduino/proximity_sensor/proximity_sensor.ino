/*
 * Arduino Proximity Sensor for Music-IO
 * 
 * This code reads data from an HC-SR04 ultrasonic proximity sensor
 * and sends the distance measurements to the computer via serial port.
 * 
 * Hardware Setup:
 * - HC-SR04 VCC -> Arduino 5V
 * - HC-SR04 GND -> Arduino GND
 * - HC-SR04 TRIG -> Arduino Pin 9
 * - HC-SR04 ECHO -> Arduino Pin 10
 * 
 * The sensor measures distances from 2cm to 400cm
 * Data is sent as JSON: {"distance": 25.5}
 */

// Pin definitions
const int TRIG_PIN = 9;
const int ECHO_PIN = 10;
const int LED_PIN = 13;  // Built-in LED for status indication

// Configuration
const int MEASUREMENT_INTERVAL = 50;  // Milliseconds between measurements
const int MAX_DISTANCE = 400;         // Maximum distance in cm
const int MIN_DISTANCE = 2;           // Minimum distance in cm
const int SMOOTHING_SAMPLES = 3;      // Number of samples for smoothing

// Variables
float distanceBuffer[SMOOTHING_SAMPLES];
int bufferIndex = 0;
unsigned long lastMeasurement = 0;
bool ledState = false;

void setup() {
  // Initialize serial communication
  Serial.begin(9600);
  
  // Initialize pins
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(LED_PIN, OUTPUT);
  
  // Initialize distance buffer
  for (int i = 0; i < SMOOTHING_SAMPLES; i++) {
    distanceBuffer[i] = 0;
  }
  
  // Startup indication
  blinkLED(3, 200);
  
  // Send ready message
  Serial.println("{\"status\":\"ready\"}");
}

void loop() {
  unsigned long currentTime = millis();
  
  // Check if it's time for a new measurement
  if (currentTime - lastMeasurement >= MEASUREMENT_INTERVAL) {
    lastMeasurement = currentTime;
    
    // Measure distance
    float distance = measureDistance();
    
    // Validate and smooth the measurement
    if (distance >= MIN_DISTANCE && distance <= MAX_DISTANCE) {
      // Add to buffer for smoothing
      distanceBuffer[bufferIndex] = distance;
      bufferIndex = (bufferIndex + 1) % SMOOTHING_SAMPLES;
      
      // Calculate smoothed distance
      float smoothedDistance = getSmoothedDistance();
      
      // Send data to computer
      sendDistance(smoothedDistance);
      
      // Blink LED to show activity
      toggleLED();
    }
  }
  
  // Check for incoming commands (for future use)
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    handleCommand(command);
  }
}

/**
 * Measure distance using HC-SR04 sensor
 * Returns distance in centimeters
 */
float measureDistance() {
  // Clear the trigger pin
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  
  // Send 10 microsecond pulse to trigger
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  // Read the echo pin
  // pulseIn returns the duration in microseconds
  long duration = pulseIn(ECHO_PIN, HIGH, 30000);  // 30ms timeout
  
  // Calculate distance
  // Speed of sound is 343 m/s or 0.0343 cm/microsecond
  // Distance = (duration * speed) / 2 (divide by 2 for round trip)
  float distance = (duration * 0.0343) / 2.0;
  
  // Return 0 if timeout or invalid reading
  if (duration == 0 || distance > MAX_DISTANCE) {
    return 0;
  }
  
  return distance;
}

/**
 * Calculate smoothed distance using moving average
 */
float getSmoothedDistance() {
  float sum = 0;
  int validSamples = 0;
  
  for (int i = 0; i < SMOOTHING_SAMPLES; i++) {
    if (distanceBuffer[i] > 0) {
      sum += distanceBuffer[i];
      validSamples++;
    }
  }
  
  if (validSamples > 0) {
    return sum / validSamples;
  }
  
  return 0;
}

/**
 * Send distance data to computer via serial
 * Format: JSON {"distance": 25.5}
 */
void sendDistance(float distance) {
  Serial.print("{\"distance\":");
  Serial.print(distance, 1);  // 1 decimal place
  Serial.println("}");
}

/**
 * Toggle LED state
 */
void toggleLED() {
  ledState = !ledState;
  digitalWrite(LED_PIN, ledState ? HIGH : LOW);
}

/**
 * Blink LED for visual feedback
 */
void blinkLED(int times, int delayMs) {
  for (int i = 0; i < times; i++) {
    digitalWrite(LED_PIN, HIGH);
    delay(delayMs);
    digitalWrite(LED_PIN, LOW);
    delay(delayMs);
  }
}

/**
 * Handle incoming commands from computer
 * For future expansion (calibration, configuration, etc.)
 */
void handleCommand(String command) {
  command.trim();
  
  if (command == "ping") {
    Serial.println("{\"response\":\"pong\"}");
  }
  else if (command == "status") {
    Serial.print("{\"status\":\"running\",\"interval\":");
    Serial.print(MEASUREMENT_INTERVAL);
    Serial.println("}");
  }
  else if (command == "test") {
    blinkLED(5, 100);
    Serial.println("{\"response\":\"test_complete\"}");
  }
  else {
    Serial.print("{\"error\":\"unknown_command\",\"command\":\"");
    Serial.print(command);
    Serial.println("\"}");
  }
}
