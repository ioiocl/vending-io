/*
 * Button Controller for Music-IO
 * Sends button press events via serial
 * 
 * Output format: JSON
 * {"button": "pressed"} or {"button": "released"}
 * 
 * Upload to Arduino on COM7
 */

const int buttonPin = 9;  // Joystick SW connected to pin 9

int lastButtonState = HIGH;  // Button is active LOW
int currentButtonState = HIGH;
unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 50;  // 50ms debounce

void setup() {
  Serial.begin(9600);
  pinMode(buttonPin, INPUT_PULLUP);  // Button is active LOW
  
  Serial.println("{\"status\": \"ready\"}");
}

void loop() {
  int reading = digitalRead(buttonPin);
  
  // Check if button state changed
  if (reading != lastButtonState) {
    lastDebounceTime = millis();
  }
  
  // If enough time has passed, update the button state
  if ((millis() - lastDebounceTime) > debounceDelay) {
    // If state has changed
    if (reading != currentButtonState) {
      currentButtonState = reading;
      
      // Send event when button is pressed (LOW)
      if (currentButtonState == LOW) {
        Serial.println("{\"button\": \"pressed\"}");
      } else {
        Serial.println("{\"button\": \"released\"}");
      }
    }
  }
  
  lastButtonState = reading;
  delay(10);  // Small delay to reduce CPU usage
}
