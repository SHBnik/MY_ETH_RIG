#include <Arduino.h>


uint8_t pin_map[14] = {3,A0,8,A2,9,6,A1,7,2,5,A3,4,A4,A5}; 


void pin_init();
void report(uint8_t fan_num,uint8_t fan_stat);


void setup() {
  Serial.begin(9600);
  pin_init();

  Serial.println("Arduino ON");
}

void loop() {
  uint8_t fan_number, fan_status;
  if(Serial.available()){
    fan_number =  Serial.readStringUntil(',').toInt();
    fan_status = Serial.readStringUntil('\n').toInt();
    report(fan_number,fan_status);
    if(fan_number >= 0 && fan_number <= 14){
      if(fan_status == 0){
        digitalWrite(pin_map[fan_number],HIGH);
      }
      else if(fan_status == 1){
        digitalWrite(pin_map[fan_number],LOW);
      }
    }
  }
}




void pin_init(){
  for (size_t i = 0; i < 14; i++){
    pinMode(pin_map[i],OUTPUT);
    digitalWrite(pin_map[i],HIGH);
  }
  
}


void report(uint8_t fan_num,uint8_t fan_stat){
  Serial.print("fan ");
  Serial.print(fan_num);
  Serial.print(" is:");
  Serial.println(fan_stat);
  
}