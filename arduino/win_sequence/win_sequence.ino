#include <Servo.h>

Servo myServo;

const int servoPin = 9;

// Para servos de 360° (continuos)
const int leftSpeed  = 0;    // Máxima velocidad izquierda
const int rightSpeed = 180;  // Máxima velocidad derecha
const int stopServo  = 90;   // Parar completamente (ajustar a 89/91 si no se detiene)

const int moveTime = 3000;   // 3 segundos movimiento
const int stopTime = 3000;   // 3 segundos parada

void setup() {
  Serial.begin(9600);
  myServo.attach(servoPin);

  // Iniciar parado
  myServo.write(stopServo);
  Serial.println("Servo DS04-NFC 360° inicializado (WIN/RUN para ejecutar)");
  delay(500);
}

void loop() {
  // Esperar señal por Serial
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd.equalsIgnoreCase("WIN") || cmd.equalsIgnoreCase("RUN")) {
      ejecutarSecuencia();
      Serial.println("SECUENCIA_COMPLETADA");
    } else if (cmd.equalsIgnoreCase("STOP")) {
      myServo.write(stopServo);
      Serial.println("MOTOR_PARADO");
    } else if (cmd.equalsIgnoreCase("LEFT")) {
      myServo.write(leftSpeed);
      Serial.println("GIRO_IZQUIERDA_CONTINUO");
    } else if (cmd.equalsIgnoreCase("RIGHT")) {
      myServo.write(rightSpeed);
      Serial.println("GIRO_DERECHA_CONTINUO");
    }
  }
}

void ejecutarSecuencia() {
  // Girar en una dirección (izquierda) - 3 segundos
  Serial.println("Girando IZQUIERDA (360°) 3s...");
  myServo.write(leftSpeed);
  delay(moveTime);

  // Parar - 3 segundos
  Serial.println("PARADO 3s...");
  myServo.write(stopServo);
  delay(stopTime);

  // Girar en dirección contraria (derecha) - 3 segundos
  Serial.println("Girando DERECHA (360°) 3s...");
  myServo.write(rightSpeed);
  delay(moveTime);

  // Parar
  Serial.println("PARADO");
  myServo.write(stopServo);
}
