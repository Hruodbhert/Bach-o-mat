#include <Wire.h>
#include <Servo.h>
#include <EEPROM.h>

#define INDIRIZZO_MANO 4    // I2C address (to be changed from 0 (lowest octave) to 4 (highest octave) in the five different Arduino Nano boards

#define NOTE_PER_MANO 12   // Number of servos controlled by each Arduino Nano board

#define OFFSET_INDIRIZZI 8  // Offset applied to I2C addresses (the first 8 addresses are reserved by I2C standards)

#define SAFE_START_ANGLE 145

#define CALIBRATION_MODE_PIN A0  //Pin for calibration/play mode switch (HIGH=setup, LOW=play)
#define SOGLIA 512 // Threshold for analog to digital conversion (in 0 or 1) (Arduino Nano has a resolution of 10 bits => 1024 values)

Servo dito[NOTE_PER_MANO];

int angle[NOTE_PER_MANO][2];
byte note;
bool state;
bool setup_state[NOTE_PER_MANO];

///////////////////////////////////////////
////////////////SETUP FUNCTIONS
///////////////////////////////////////////

void handle_setup() {
  byte operation = Wire.read();
  byte servo_num = Wire.read();
  byte data_1 = Wire.read();
  byte data_2;
  if (operation != 1) {
    data_2 = Wire.read();
  }
  switch ((int) operation) {
    case 1: // Push/Release
      setup_state[servo_num] = (data_1 == 1);
      push(servo_num, setup_state[servo_num]);
      break;
    case 2: // Set angles
      angle[servo_num][0] = (int)data_1; //  off_angle
      angle[servo_num][1] = (int)(data_1 - data_2); //  on_angle = off_angle - delta_angle
      push(servo_num, setup_state[servo_num]);
      break;
    case 3: // Set and save angles
      // Set
      angle[servo_num][0] = (int)data_1; //  off_angle
      angle[servo_num][1] = (int)(data_1 - data_2); //  on_angle = off_angle - delta_angle
      push(servo_num, setup_state[servo_num]);
      // Save
      // EEPROM organized in this way : [off_angle_0, on_angle_0, off_angle_1, on_angle_1,... off_angle_11, on_angle_11]
      EEPROM.update(2 * servo_num, data_1);
      EEPROM.update(2 * servo_num + 1, data_1 - data_2);
      break;
    default:
      break;
  }
}

///////////////////////////////////////////
////////////////PLAY FUNCTIONS
///////////////////////////////////////////

void push(byte servo_num, bool state) {
  dito[servo_num].write(angle[servo_num][state]);
  return;
}

////////////////////////////

void play() {
  byte c = Wire.read();
  note = c % NOTE_PER_MANO;
  state = !(bool(c / NOTE_PER_MANO));
  push(note, state);
}

////////////////////////////
void get_angles_from_EEPROM() {
  for (int i = 0; i < NOTE_PER_MANO; i++) {
    angle[i][0] = EEPROM.read(2 * i);
    angle[i][1] = EEPROM.read(2 * i + 1);
  }
}
///////////////////////////////////

void setup() {

  //Attach Servos
  //Arduino NANO
  for (int i = 0; i < NOTE_PER_MANO; i++) {
    dito[i].attach(i + 2);
    dito[i].write(SAFE_START_ANGLE);
    setup_state[i] = 0;
  }
  // Get angles from EEPROM
  get_angles_from_EEPROM();

  //CALIBRATION MODE
  if (analogRead(CALIBRATION_MODE_PIN) > SOGLIA) { //CALIBRATION MODE
    Wire.begin(INDIRIZZO_MANO + OFFSET_INDIRIZZI);
    Wire.onReceive(handle_setup);
    while (analogRead(CALIBRATION_MODE_PIN) > SOGLIA) {
      delay(20);
    }
    Wire.end();
    // Get angles from EEPROM
    get_angles_from_EEPROM();
  }
  //END OF CALIBRATION

  //Set Servos OFF
  for (byte i = 0; i < NOTE_PER_MANO; i++) {
    push(i, '\0');
  }

  Wire.begin(INDIRIZZO_MANO + OFFSET_INDIRIZZI);
  Wire.onReceive(play);
}

void loop() {
  delay(5);
}
