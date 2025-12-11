/*
 * SIMPLE BUTTON TEST for COM7
 * Upload this to your Arduino on COM7
 * 
 * Wiring:
 * - Button one side to pin 9
 * - Button other side to GND
 * - (Internal pullup resistor is used)
 */

const int buttonPin = 9;

void setup() {
  Serial.begin(9600);
  pinMode(buttonPin, INPUT_PULLUP);  // Button pulls to GND when pressed
  
  Serial.println("Button Test Ready!");
  Serial.println("Press the button...");
}

void loop() {
  int buttonState = digitalRead(buttonPin);
  
  // Button is pressed when LOW (connected to GND)
  if (buttonState == LOW) {
    Serial.println("BUTTON PRESSED!");
    delay(500);  // Debounce delay
  }
  
  delay(50);  // Small delay
}
