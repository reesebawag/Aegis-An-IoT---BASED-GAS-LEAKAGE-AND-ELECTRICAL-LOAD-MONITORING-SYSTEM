#include <Wire.h>
#include <Adafruit_ADS1X15.h>

Adafruit_ADS1115 ads;

const int buzzer = 9;
int Relay = 2;
const int led = 13;

const float FACTOR = 13;
const float multiplier = 0.0625F;

const int sensorPin = A0;
const int numSamples = 100;

bool highCurrentDetected = false;
unsigned long relayActivationTime = 0;
const unsigned long relayActivationDuration = 3000; // Duration in milliseconds

void setup() {
  Serial.begin(9600);
  ads.begin(0x48);
  ads.setGain(GAIN_TWO);
  pinMode(buzzer, OUTPUT);
  pinMode(led, OUTPUT);
  pinMode(Relay, OUTPUT);
}

void loop() {
  float CurrentRMS = getCurrent(); // You need to define the getCurrent function.
  
  Serial.println(CurrentRMS, 2);
 
  if (CurrentRMS > 0.2) {
    if (!highCurrentDetected) {
      highCurrentDetected = true;
      digitalWrite(buzzer, HIGH);
      digitalWrite(led, HIGH);
      relayActivationTime = millis();
      digitalWrite(Relay, HIGH); // Turn on the relay
    }

    if (millis() - relayActivationTime >= relayActivationDuration) {
      highCurrentDetected = false;
      digitalWrite(buzzer, LOW); // Ensure the buzzer is off if Power is not greater than 5
      digitalWrite(led, LOW);
      digitalWrite(Relay, LOW); // Turn off the relay
    }
  }
}

void PrintMeasurement(String prefix, float value, String postfix) {
  Serial.println(prefix);
  Serial.print(value, 2);
  Serial.println(postfix);
}

float getCurrent() {
  float Volt_differential;
  float current;
  float sum = 0;
  long time = millis();
  int counter = 0;

  while (millis() - time < 1000) {
    Volt_differential = ads.readADC_Differential_0_1() * multiplier;
    current = Volt_differential * FACTOR;
    current /= 1000.0;
    sum += sq(current);
    counter = counter + 1;
  }
  current = sqrt(sum / counter);
  return current;
}
