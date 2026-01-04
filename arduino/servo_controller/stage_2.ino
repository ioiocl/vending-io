/*
 * STAGE 2 - Pump Controller (COM4)
 * 
 * Receives pump activation/deactivation signals via serial from Python
 * Controls suction pump and solenoid valve
 * Supports configurable suction strength
 */

#include <Servo.h>

Servo bomba;    // Pump servo
Servo valvula;  // Valve servo

// Serial buffer
String inputBuffer = "";

// State
bool pumpActive = false;
int suctionLevel = 60;  // Default: medium suction (0=max, 90=off)

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
  
  // Turn pump ON with configured suction level
  bomba.write(suctionLevel);
  delay(100);  // Let it start
  
  pumpActive = true;
  Serial.print("{\"status\":\"pump_active\",\"suction_level\":");
  Serial.print(suctionLevel);
  Serial.println("}");
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
        
        if (inputBuffer.startsWith("ACTIVATE_PUMP")) {
          // Check if suction level is specified: ACTIVATE_PUMP:45
          int colonPos = inputBuffer.indexOf(':');
          if (colonPos > 0) {
            String levelStr = inputBuffer.substring(colonPos + 1);
            int level = levelStr.toInt();
            if (level >= 0 && level <= 90) {
              suctionLevel = level;
              Serial.print("{\"status\":\"suction_level_set\",\"level\":");
              Serial.print(suctionLevel);
              Serial.println("}");
            }
          }
          activatePump();
        }
        else if (inputBuffer == "DEACTIVATE_PUMP") {
          deactivatePump();
        }
        else if (inputBuffer.startsWith("SET_SUCTION")) {
          // SET_SUCTION:45
          int colonPos = inputBuffer.indexOf(':');
          if (colonPos > 0) {
            String levelStr = inputBuffer.substring(colonPos + 1);
            int level = levelStr.toInt();
            if (level >= 0 && level <= 90) {
              suctionLevel = level;
              Serial.print("{\"status\":\"suction_level_set\",\"level\":");
              Serial.print(suctionLevel);
              Serial.println("}");
            } else {
              Serial.println("{\"error\":\"invalid_suction_level\"}");
            }
          }
        }
        else if (inputBuffer == "STATUS") {
          if (pumpActive) {
            Serial.print("{\"status\":\"pump_active\",\"suction_level\":");
            Serial.print(suctionLevel);
            Serial.println("}");
          } else {
            Serial.print("{\"status\":\"pump_inactive\",\"suction_level\":");
            Serial.print(suctionLevel);
            Serial.println("}");
          }
        }
        else if (inputBuffer == "RESET") {
          deactivatePump();
          suctionLevel = 60;  // Reset to default
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
