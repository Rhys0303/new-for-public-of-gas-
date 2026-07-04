#include <Arduino.h>
void setup() { 
  Serial.begin(9600); 
} 
  
void loop() { 
  float sensorValue=0; 
 
//Average   
    for(int x = 0 ; x < 100 ; x++) 
  { 
    sensorValue = sensorValue + analogRead(A0); 
  } 
  sensorValue = sensorValue/100.0; 
//-----------------------------------------------/ 
  Serial.println(sensorValue);
  delay(1000); 

}