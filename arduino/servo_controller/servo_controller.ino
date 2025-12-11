/*
 * Servo Controller for Music-IO
 * Controls one 360° continuous rotation servo based on serial commands
 * 
 * Commands:
 * - "LEFT_MOTOR" - Move LEFT for 5 sec
 * - "RIGHT_MOTOR" - Move RIGHT for 5 sec
 * - "GATE_OPEN" - Move LEFT continuously (until STOP)
 * - "GATE_CLOSE" - Move RIGHT continuously (until STOP)
 * - "GATE_SEQUENCE" - 3s left, 3s stop, 3s right (runs once per win)
 * - "WIN" - Alias to run the same sequence once
 * - "STOP" - Stop motor immediately (90°)
 * 
 * Upload to Arduino MEGA on COM4
 */

#include <Servo.h>

Servo servo1;
// Continuous servo absolute angles (adjust if needed)
const int LEFT_SPEED  = 0;    // max left
const int RIGHT_SPEED = 180;  // max right
const int STOP_POS    = 90;   // stop (neutral)

bool motorActive = false;
unsigned long motorStartTime = 0;
unsigned long motorDuration = 5000;  // 5 seconds
String currentMotor = "";

void setup() {
  Serial.begin(9600);
  servo1.attach(9);
  
  // Start in neutral position
  servo1.write(STOP_POS);
  
  Serial.println("Servo Controller Ready");
}

void loop() {
  // Check for serial commands
  if (Serial.available() > 0) {
    String command = Serial.readStringUntil('\n');
    command.trim();
    
    if (command == "LEFT_MOTOR") {
      activateLeftMotor();
    } 
    else if (command == "RIGHT_MOTOR") {
      activateRightMotor();
    }
    else if (command == "GATE_OPEN") {
      gateOpen();
    }
    else if (command == "GATE_CLOSE") {
      gateClose();
    }
    else if (command == "GATE_SEQUENCE") {
      gateSequence();
    }
    else if (command == "WIN") {
      gateSequence();
    }
    else if (command == "STOP") {
      stopMotors();
    }
  }
  
  // Check if motor cycle is complete
  if (motorActive && (millis() - motorStartTime >= motorDuration)) {
    stopMotors();
    Serial.println("MOTOR_COMPLETE");
  }
}

void activateLeftMotor() {
  motorActive = true;
  motorStartTime = millis();
  currentMotor = "LEFT";
  
  servo1.write(LEFT_SPEED);  // Move LEFT
  
  Serial.println("LEFT_MOTOR_ACTIVE");
}

void activateRightMotor() {
  motorActive = true;
  motorStartTime = millis();
  currentMotor = "RIGHT";
  
  servo1.write(RIGHT_SPEED);  // Move RIGHT
  
  Serial.println("RIGHT_MOTOR_ACTIVE");
}

void stopMotors() {
  motorActive = false;
  currentMotor = "";
  
  // Return to neutral
  servo1.write(STOP_POS);
  
  Serial.println("MOTORS_STOPPED");
}

void gateOpen() {
  // Move servo one direction to open gate
  // No timer - Python controls the duration
  servo1.write(LEFT_SPEED);
  
  Serial.println("GATE_OPENING");
}

void gateClose() {
  // Move servo opposite direction to close gate
  // No timer - Python controls the duration
  servo1.write(RIGHT_SPEED);
  
  Serial.println("GATE_CLOSING");
}

void gateSequence() {
  // 3s left, 3s stop, 3s right (single run)
  Serial.println("GATE_SEQUENCE_START");
  
  // Left 3s
  servo1.write(LEFT_SPEED);
  delay(3000);
  
  // Stop 3s
  servo1.write(STOP_POS);
  delay(3000);
  
  // Right 3s
  servo1.write(RIGHT_SPEED);
  delay(3000);
  
  // Stop
  servo1.write(STOP_POS);
  Serial.println("GATE_SEQUENCE_DONE");
}
