/*
 * STAGE 2 - Pump Controller (COM4)
 * 
 * Receives pump activation/deactivation signals via serial from Python
 * Controls suction pump and solenoid valve
 */

#include <Servo.h>

Servo bomba;    // Pump servo
Servo valvula;  // Valve servo

// Serial buffer
String inputBuffer = "";

// State
bool pumpActive = false;

void setup() {
  Serial.begin(9600);
  
  bomba.attach(9); 
  valvula.attach(10);
  
  // Initialize to OFF state
  bomba.write(90);    // Pump OFF
  valvula.write(90);  // Valve closed
  
  Serial.println("{\"status\":\"pump_ready\"}");
}

void activatePump() {
  Serial.println("{\"status\":\"pump_activating\"}");
  
  // Open valve first
  valvula.write(180);
  delay(200);
  
  // Turn pump ON (suction) - 0 = full speed
  bomba.write(0);
  delay(100);  // Let it start
  
  pumpActive = true;
  Serial.println("{\"status\":\"pump_active\"}");
}

void deactivatePump() {
  Serial.println("{\"status\":\"pump_deactivating\"}");
  
  // Turn pump OFF
  bomba.write(90);
  delay(1000);  // Wait for release
  
  // Close valve
  valvula.write(90);
  
  pumpActive = false;
  Serial.println("{\"status\":\"pump_inactive\"}");
}

void loop() {
  // Check for serial commands from Python
  while (Serial.available() > 0) {
    char c = Serial.read();
    if (c == '\n' || c == '\r') {
      if (inputBuffer.length() > 0) {
        inputBuffer.trim();
        
        // Debug: show received command
        Serial.print("{\"received\":\"");
        Serial.print(inputBuffer);
        Serial.println("\"}");
        
        if (inputBuffer == "ACTIVATE_PUMP") {
          activatePump();
        }
        else if (inputBuffer == "DEACTIVATE_PUMP") {
          deactivatePump();
        }
        else if (inputBuffer == "STATUS") {
          if (pumpActive) {
            Serial.println("{\"status\":\"pump_active\"}");
          } else {
            Serial.println("{\"status\":\"pump_inactive\"}");
          }
        }
        else if (inputBuffer == "RESET") {
          deactivatePump();
          Serial.println("{\"status\":\"pump_reset\"}");
        }
        else if (inputBuffer == "TEST") {
          // Quick test cycle
          Serial.println("{\"status\":\"test_starting\"}");
          activatePump();
          delay(3000);
          deactivatePump();
          Serial.println("{\"status\":\"test_complete\"}");
        }
        
        inputBuffer = "";
      }
    } else {
      inputBuffer += c;
    }
  }
  
  delay(10);
}
