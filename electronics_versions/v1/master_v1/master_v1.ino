#include <MIDIUSB.h>
#include <Wire.h>


#define NOTE_PER_MANO 12 // Number of servos controlled by each Arduino Nano board
#define N_MANI 5 // Number of Arduino Nano boards on the bus for controlling the servos
#define OFFSET_INDIRIZZI 8  // Offset applied to I2C addresses (the first 8 addresses are reserved by I2C standards)

#define CALIBRATION_MODE_PIN 8 //Pin for calibration/play mode switch (HIGH=setup, LOW=play)


byte note;
long j;
bool state;


//////////////////////////////////////
int mano_from_servo(byte servo_num) {
  for (int i = 0; i < N_MANI; i++) {
    if (servo_num >= i * NOTE_PER_MANO && servo_num < (i + 1)*NOTE_PER_MANO) {
      return i;
    }
  }
}
//////////////////////////////////////
void play(byte note, bool state) {
  // Keyboard's extension is from MIDI notes 36 to 93
  while (note < 36) {
    note = note + 12;
  }
  while (note > 93) {
    note = note - 12;
  }
  note = note - 36;
  Wire.beginTransmission(mano_from_servo(note) + OFFSET_INDIRIZZI);
  Wire.write((note % NOTE_PER_MANO) + 12 * (!state));
  Wire.endTransmission();

}
////////////////////

void noteOn(byte channel, byte pitch, byte velocity) {
  if (velocity != 0) {
    Serial.print("Note On: ");
    Serial.print(pitch, DEC);
    Serial.print(", channel=");
    Serial.print(channel);
    Serial.print(", velocity=");
    Serial.println(velocity);
    play(pitch, 1);

  } else {
    noteOff(channel, pitch, velocity);
  }
}

void noteOff(byte channel, byte pitch, byte velocity) {
  Serial.print("Note Off: ");
  Serial.print(pitch, DEC);
  Serial.print(", channel=");
  Serial.print(channel);
  Serial.print(", velocity=");
  Serial.println(velocity);
  play(pitch, 0);
}
/////////////////////////////////
void handle_setup() {

  byte operation;
  byte servo_num;
  byte data_1;
  byte data_2;

  while (Serial.available()) {
    operation = Serial.read();
    servo_num = Serial.read();
    data_1 = Serial.read();
    Wire.beginTransmission(mano_from_servo(servo_num) + OFFSET_INDIRIZZI);
    Wire.write(operation);
    Wire.write(servo_num % NOTE_PER_MANO);
    Wire.write(data_1);
    if (operation != 1) {
      data_2 = Serial.read();
      Wire.write(data_2);
    }
    Wire.endTransmission();
  }
}
//////////////////////////////////
void setup() {
  pinMode(CALIBRATION_MODE_PIN, INPUT);
  pinMode(LED_BUILTIN, OUTPUT);
  digitalWrite(LED_BUILTIN, HIGH);
  Serial.begin(9600);
  Wire.begin();
  while (digitalRead(CALIBRATION_MODE_PIN)) {
    handle_setup();
    delay(10);
  }
  digitalWrite(LED_BUILTIN, LOW);
}

void loop() {
  midiEventPacket_t rx = MidiUSB.read();
  switch (rx.header) {
    case 0:
      break; // No pending events

    case 0x9:
      noteOn(
        rx.byte1 & 0xF,  //channel
        rx.byte2,        //pitch
        rx.byte3         //velocity
      );
      break;

    case 0x8:
      noteOff(
        rx.byte1 & 0xF,  //channel
        rx.byte2,        //pitch
        rx.byte3         //velocity
      );
      break;

    default:
      Serial.print("Unhandled MIDI message: ");
      Serial.print(rx.header, HEX);
      Serial.print("-");
      Serial.print(rx.byte1, HEX);
      Serial.print("-");
      Serial.print(rx.byte2, HEX);
      Serial.print("-");
      Serial.println(rx.byte3, HEX);
  }
}
