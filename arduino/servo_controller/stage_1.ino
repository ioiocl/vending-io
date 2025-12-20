/*
 * STAGE 1 - Main Robotic Sequence Controller (COM7)
 * 
 * Flow:
 * 1. Button press → SG90 dance (game initiation)
 * 2. Wait for WIN signal from Python
 * 3. On WIN: DS04 360° sequence → Arm pick-down → Signal pump → Arm lift
 * 4. Reset and wait for next button press
 */

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pca = Adafruit_PWMServoDriver();

// Button
const int buttonPin = 9;
int lastButtonState = HIGH;
int currentButtonState = HIGH;
unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 50;

// Proximity Sensor (HC-SR04)
#define TRIGGER_PIN 7
#define ECHO_PIN    6
#define DIST_THRESHOLD 50  // cm
long duration;
int distance;
bool lastProximityState = false;  // Track if invite text is shown
unsigned long lastProximityCheck = 0;
const unsigned long proximityInterval = 200;  // Check every 200ms

// Relay
#define RELAY_PIN 8
bool relayOpen = false;

// LED (Pin 10)
const int LED_PIN = 10;

// State machine
enum State {
  IDLE,
  GAME_STARTED,
  WAITING_FOR_RESULT,
  WIN_SEQUENCE
};
State currentState = IDLE;

unsigned long lastServo360StopMs = 0;
const unsigned long servo360StopIntervalMs = 100;

// === SG90 Servos (pins 0 and 1) ===
#define SG90_MIN 150
#define SG90_MAX 600
#define SG90_1 0
#define SG90_2 1

// === DS04-NFC 360° Servo ===
#define SERVO360 3
#define PWM_STOP        307

// ================= SPEED DEFINITIONS =================
// Fast speed (used in STEP 1 and STEP 3)
#define SPEED_FAST_OFFSET 60

#define PWM_RIGHT_FAST (PWM_STOP - SPEED_FAST_OFFSET)
#define PWM_LEFT_FAST  (PWM_STOP + SPEED_FAST_OFFSET)

// === KS3518 Servos (Arm) ===
#define KS_MIN 110
#define KS_MAX 550

#define BASE_SERVO       8
#define LOWER_LEFT       9
#define LOWER_RIGHT     10
#define UPPER_ARM       11

// === COLLAPSED START POSITIONS (FULL COLLAPSE) ===
#define BASE_HOME         90   // Base centered
#define LOWER_LEFT_HOME    0   // Collapse down
#define LOWER_RIGHT_HOME   0   // Collapse down
#define UPPER_HOME        10   // Collapse upper

// === ARM EXTENDED POSITIONS ===
#define LOWER_ARMS_FORWARD 90  // Lower arms forward 90°
#define UPPER_ARM_ALIGNED  90  // Upper arm aligned for pick
#define LOWER_ARMS_PICK    101
#define LOWER_ARMS_REACH   136
#define FOREARM_FORWARD_35 136
#define FOREARM_DOWN_20    116
#define LEFT_LOWER_DOWN_45 71
#define LEFT_LOWER_DOWN_90 26
#define BASE_LEFT_ROTATED  15  // Base rotated 75° left (90 - 75 = 15)
#define BASE_LEFT_ROTATED_15 75  // Base rotated 15° left (90 - 15 = 75)

// Serial buffer
String inputBuffer = "";

// Map angles
int sg90Pulse(int angle) { return map(angle, 0, 180, SG90_MIN, SG90_MAX); }
int ksPulse(int angle)   { return map(angle, 0, 180, KS_MIN, KS_MAX); }

// Smooth KS movement
void moveKS(int channel, int startAngle, int endAngle, int stepDelay = 10) {
  int startP = ksPulse(startAngle);
  int endP   = ksPulse(endAngle);

  if (startP < endP) {
    for (int p = startP; p <= endP; p++) {
      pca.setPWM(channel, 0, p);
      delay(stepDelay);
    }
  } else {
    for (int p = startP; p >= endP; p--) {
      pca.setPWM(channel, 0, p);
      delay(stepDelay);
    }
  }
}

// SG90 random movement
void moveServoRandom(int channel) {
  int angle = random(20, 160);
  pca.setPWM(channel, 0, sg90Pulse(angle));
}

// Random LED blink during SG90 dance (non-blocking)
void initDanceLed(unsigned long &lastToggleMs, unsigned long &toggleIntervalMs, bool &ledStateHigh) {
  ledStateHigh = true;
  digitalWrite(LED_PIN, HIGH);
  lastToggleMs = millis();
  toggleIntervalMs = random(100, 2000);
}

void updateDanceLed(unsigned long &lastToggleMs, unsigned long &toggleIntervalMs, bool &ledStateHigh) {
  unsigned long now = millis();
  if (now - lastToggleMs >= toggleIntervalMs) {
    ledStateHigh = !ledStateHigh;
    digitalWrite(LED_PIN, ledStateHigh ? HIGH : LOW);
    lastToggleMs = now;
    toggleIntervalMs = ledStateHigh ? random(100, 2000) : random(100, 1000);
  }
}

// Robotic arm sequence - WITH ANTEBRAZO DOWN MOVEMENT
void performArmSequence() {
  Serial.println("{\"status\":\"arm_sequence_start\"}");
  
  // STEP 1 — Move lower arms forward
  Serial.println("{\"status\":\"arm_step_1_lower_arms_forward\"}");
  moveKS(LOWER_LEFT, LOWER_LEFT_HOME, LOWER_ARMS_FORWARD, 7);
  moveKS(LOWER_RIGHT, LOWER_RIGHT_HOME, LOWER_ARMS_FORWARD, 7);
  
  // STEP 2 — Move upper arm to aligned position
  Serial.println("{\"status\":\"arm_step_2_align_upper_arm\"}");
  moveKS(UPPER_ARM, UPPER_HOME, UPPER_ARM_ALIGNED, 7);
  
  // STEP 3 — Move arms FORWARD to pick position
  Serial.println("{\"status\":\"arm_step_3_pick_position\"}");
  moveKS(LOWER_LEFT, LOWER_ARMS_FORWARD, LOWER_ARMS_PICK, 7);
  moveKS(LOWER_RIGHT, LOWER_ARMS_FORWARD, LOWER_ARMS_PICK, 7);
  
  // STEP 4 — Move forearm forward 35° from pick position
  Serial.println("{\"status\":\"arm_step_4_forearm_forward\"}");
  moveKS(LOWER_LEFT, LOWER_ARMS_PICK, LOWER_ARMS_REACH, 7);
  moveKS(LOWER_RIGHT, LOWER_ARMS_PICK, LOWER_ARMS_REACH, 7);
  
  // STEP 5 — Move forearm down 20°
  Serial.println("{\"status\":\"arm_step_5_forearm_down_20\"}");
  moveKS(LOWER_LEFT, LOWER_ARMS_REACH, FOREARM_DOWN_20, 7);
  moveKS(LOWER_RIGHT, LOWER_ARMS_REACH, FOREARM_DOWN_20, 7);
  
  // STEP 6 — Move left lower servo down 45°
  Serial.println("{\"status\":\"arm_step_6_left_down_45\"}");
  moveKS(LOWER_LEFT, FOREARM_DOWN_20, LEFT_LOWER_DOWN_45, 7);
  
  // Pre STEP 7 — Rotate base 30° left
  Serial.println("{\"status\":\"arm_pre_step_7_base_left_30\"}");
  moveKS(BASE_SERVO, BASE_HOME, BASE_LEFT_ROTATED_15, 7);

  // STEP 7 — Move left lower servo down an additional 45° (90° total)
  Serial.println("{\"status\":\"arm_step_7_left_down_90_activate_pump\"}");
  moveKS(LOWER_LEFT, LEFT_LOWER_DOWN_45, LEFT_LOWER_DOWN_90, 7);
  delay(100);
  signalPythonForPump(true);
  
  delay(5000);

  // STEP 8 — Return forearm to forward position
  Serial.println("{\"status\":\"arm_step_8_return_forearm\"}");
  moveKS(LOWER_LEFT, LEFT_LOWER_DOWN_90, LOWER_ARMS_FORWARD, 7);
  moveKS(LOWER_RIGHT, FOREARM_DOWN_20, LOWER_ARMS_FORWARD, 7);

  delay(100);
  signalPythonForPump(false);
  
  // STEP 9 — Rotate base left
  Serial.println("{\"status\":\"arm_step_9_rotate_base_left\"}");
  moveKS(BASE_SERVO, BASE_LEFT_ROTATED_15, BASE_LEFT_ROTATED, 7);

  for (int i = 0; i < 3; i++) {
    delay(100);
    signalPythonForPump(false);
  }
  
  // STEP 10 — Hold
  Serial.println("{\"status\":\"arm_step_10_hold\"}");
  delay(3000);
  
  // STEP 11 — Collapse arm back to home
  Serial.println("{\"status\":\"arm_step_11_collapse_deactivate_pump\"}");
  delay(100);
  signalPythonForPump(false);

  pca.setPWM(BASE_SERVO,       0, ksPulse(BASE_HOME));
  pca.setPWM(LOWER_LEFT,       0, ksPulse(LOWER_LEFT_HOME));
  pca.setPWM(LOWER_RIGHT,      0, ksPulse(LOWER_RIGHT_HOME));
  pca.setPWM(UPPER_ARM,        0, ksPulse(UPPER_HOME));
  
  Serial.println("{\"status\":\"arm_sequence_complete\"}");
}

// Send signal to Python for pump/solenoid control via serial
void signalPythonForPump(bool activate) {
  if (activate) {
    Serial.println("{\"action\":\"activate_pump\"}");
    Serial.flush();
    delay(50);  // Ensure message is fully transmitted
  } else {
    Serial.println("{\"action\":\"deactivate_pump\"}");
    Serial.flush();
    delay(50);  // Ensure message is fully transmitted
  }
}

// Reset to initial state
void resetToIdle() {
  // Ensure relay is closed when returning to idle
  setRelay(false);

  // Stop 360 servo
  for (int i = 0; i < 5; i++) {
    pca.setPWM(SERVO360, 0, 0);
    delay(20);
  }

  // Collapse robot arm
  pca.setPWM(BASE_SERVO,       0, ksPulse(BASE_HOME));
  pca.setPWM(LOWER_LEFT,       0, ksPulse(LOWER_LEFT_HOME));
  pca.setPWM(LOWER_RIGHT,      0, ksPulse(LOWER_RIGHT_HOME));
  pca.setPWM(UPPER_ARM,        0, ksPulse(UPPER_HOME));

  // SG90 neutral
  pca.setPWM(SG90_1, 0, sg90Pulse(90));
  pca.setPWM(SG90_2, 0, sg90Pulse(90));

  currentState = IDLE;
  Serial.println("{\"status\":\"idle\"}");
}

// SG90 Dance sequence - initiates the game
void performSG90Dance() {
  Serial.println("{\"status\":\"sg90_dance_start\"}");
  
  unsigned long start = millis();
  unsigned long lastMoveMs = 0;
  unsigned long ledLastToggleMs = 0;
  unsigned long ledToggleIntervalMs = 0;
  bool ledStateHigh = false;

  initDanceLed(ledLastToggleMs, ledToggleIntervalMs, ledStateHigh);

  while (millis() - start < 5000) {
    unsigned long now = millis();
    if (now - lastMoveMs >= 150) {
      moveServoRandom(SG90_1);
      moveServoRandom(SG90_2);
      lastMoveMs = now;
    }

    updateDanceLed(ledLastToggleMs, ledToggleIntervalMs, ledStateHigh);
    delay(5);
  }

  digitalWrite(LED_PIN, LOW);
  
  // Return to neutral
  pca.setPWM(SG90_1, 0, sg90Pulse(90));
  pca.setPWM(SG90_2, 0, sg90Pulse(90));
  
  Serial.println("{\"status\":\"game_initiated\"}");
}

// Win sequence - everything after winning
void performWinSequence() {
  Serial.println("{\"status\":\"win_sequence_start\"}");

  for (int i = 0; i < 10; i++) {
    pca.setPWM(SERVO360, 0, PWM_STOP);
    delay(10);
  }
  
  // --------------------------------
  // STEP 1 — FAST RIGHT ROTATION
  // --------------------------------
  Serial.println("{\"status\":\"360_servo_sequence\"}");
  pca.setPWM(SERVO360, 0, PWM_RIGHT_FAST);
  delay(6000);

  // --------------------------------
  // STEP 2 — STOP (neutral)
  // --------------------------------
  Serial.println("{\"status\":\"360_servo_stop\"}");
  for (int i = 0; i < 10; i++) {
    pca.setPWM(SERVO360, 0, PWM_STOP);
    delay(10);
  }
  delay(3000);

  // --------------------------------
  // STEP 3 — FAST LEFT ROTATION
  // --------------------------------
  Serial.println("{\"status\":\"360_servo_left\"}");
  pca.setPWM(SERVO360, 0, PWM_LEFT_FAST);
  delay(3000);

  // --------------------------------
  // FINAL STOP
  // --------------------------------
  for (int i = 0; i < 10; i++) {
    pca.setPWM(SERVO360, 0, PWM_STOP);
    delay(10);
  }
  delay(2000);

  // --------------------------------
  // ARM SEQUENCE (after 360 servo)
  // --------------------------------
  performArmSequence();
  Serial.println("{\"status\":\"sequence_complete\"}");
  
  delay(2000);
  
  // Close relay when game finishes
  setRelay(false);
  
  // Reset for next round
  resetToIdle();
}

// Read distance from HC-SR04
int readDistance() {
  digitalWrite(TRIGGER_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIGGER_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIGGER_PIN, LOW);
  
  duration = pulseIn(ECHO_PIN, HIGH, 30000);  // 30ms timeout
  if (duration == 0) return -1;  // No echo received
  
  return duration * 0.034 / 2;
}

// Control relay
void setRelay(bool open) {
  if (open) {
    digitalWrite(RELAY_PIN, HIGH);
    relayOpen = true;
    Serial.println("{\"relay\":\"open\"}");
  } else {
    digitalWrite(RELAY_PIN, LOW);
    relayOpen = false;
    Serial.println("{\"relay\":\"closed\"}");
  }
}

void setup() {
  Serial.begin(9600);
  pinMode(buttonPin, INPUT_PULLUP);

  pinMode(LED_PIN, OUTPUT);
  digitalWrite(LED_PIN, LOW);
  randomSeed(analogRead(A0));
  
  // Proximity sensor pins
  pinMode(TRIGGER_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  // Relay pin
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW);  // Relay OFF initially

  pca.begin();
  pca.setPWMFreq(50);

  resetToIdle();
  Serial.println("{\"status\":\"ready\"}");
}

void loop() {
  // Check for serial commands from Python
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n') {
      inputBuffer.trim();
      
      // WIN command - accept from WAITING_FOR_RESULT or IDLE (for web-initiated games)
      if (inputBuffer == "WIN") {
        if (currentState == WAITING_FOR_RESULT || currentState == IDLE) {
          Serial.println("{\"status\":\"win_command_received\"}");
          currentState = WIN_SEQUENCE;
          performWinSequence();
        } else {
          Serial.println("{\"status\":\"win_ignored_busy\"}");
        }
      }
      // LOSE command
      else if (inputBuffer == "LOSE") {
        if (currentState == WAITING_FOR_RESULT || currentState == IDLE) {
          Serial.println("{\"status\":\"game_lost\"}");
          setRelay(false);  // Close relay when game ends
          delay(1000);
          resetToIdle();
        }
      }
      // START_GAME command - trigger SG90 dance from Python (web button)
      else if (inputBuffer == "START_GAME" && currentState == IDLE) {
        Serial.println("{\"status\":\"game_starting_from_web\"}");
        setRelay(true);  // Open relay when game starts
        currentState = GAME_STARTED;
        performSG90Dance();
        currentState = WAITING_FOR_RESULT;
      }
      // RESET command
      else if (inputBuffer == "RESET") {
        resetToIdle();
      }
      
      inputBuffer = "";
    } else {
      inputBuffer += c;
    }
  }

  // Button handling
  int reading = digitalRead(buttonPin);

  if (reading != lastButtonState)
    lastDebounceTime = millis();

  if (millis() - lastDebounceTime > debounceDelay) {
    if (reading != currentButtonState) {
      currentButtonState = reading;

      if (currentButtonState == LOW && currentState == IDLE) {
        Serial.println("{\"button\":\"pressed\"}");
        
        // Open relay when game starts
        setRelay(true);
        
        // Start game sequence
        currentState = GAME_STARTED;
        performSG90Dance();
        currentState = WAITING_FOR_RESULT;
      }
    }
  }

  lastButtonState = reading;
  
  // Proximity sensor check (only when IDLE)
  if (currentState == IDLE && millis() - lastProximityCheck >= proximityInterval) {
    lastProximityCheck = millis();
    distance = readDistance();
    
    if (distance > 0 && distance <= DIST_THRESHOLD) {
      // User is close - show invite text
      if (!lastProximityState) {
        Serial.println("{\"invite\":\"Ven a Jugar\"}");
        lastProximityState = true;
      }
    } else {
      // User is far - hide invite text
      if (lastProximityState) {
        Serial.println("{\"invite\":\"\"}");
        lastProximityState = false;
      }
    }
  }

  if (currentState != WIN_SEQUENCE && millis() - lastServo360StopMs >= servo360StopIntervalMs) {
    lastServo360StopMs = millis();
    pca.setPWM(SERVO360, 0, 0);
  }
  
  delay(10);
}
