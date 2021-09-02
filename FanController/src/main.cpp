#include <Arduino.h>


uint8_t pin_map[14] = {2,3,4,5,6,7,8,9,A1,A2,A3,A4,A5}; 





void setup() {
  Serial.begin(9600);
}

void loop() {
  uint8_t fan_number, fan_status;
  if(Serial.available()){
    fan_number =  Serial.readStringUntil(',').toInt();
    fan_status = Serial.readStringUntil('\n').toInt();
    if(fan_number >= 0 && fan_number <= 14){
      if(fan_status == 0 || fan_status == 1)
        digitalWrite(pin_map[fan_number],~fan_status);
    }
  }
}