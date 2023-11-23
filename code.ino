#include <ESP8266WiFi.h>
#include <ESP8266HTTPClient.h>
#include <OneWire.h>
#include <DallasTemperature.h>

//  ACCESS POINT CREDENTIALS
const char* ssid = "AzollaNetwork"; 
const char* password = "12345678";

// SECRET KEY
const char* SECRET_KEY = "\"ra^SWIXh(@TJe2+Js4aFfS&X+Lk3yf7\"";

// FLOAT
const int MAIN_CONTAINER_FLOAT = D6;
const int BACKUP_CONTAINER_FLOAT = D7;

// LED
const int GREEN_LED = D1; 

// RELAY
const int RELAY = D2;

// WATER TEMPERATURE SENSOR PIN
#define ONE_WIRE_BUS D5 
OneWire oneWire(ONE_WIRE_BUS);
DallasTemperature sensors(&oneWire);

// API ENDPOINT FOR ACCEPTING DATA 
const char* device_status = "http://192.168.43.71:34463/api/get_water_temp";

WiFiClient client;

//////////////////////////////////////////////////////////////////////////////

void turnGreenLedOn(){
  digitalWrite(GREEN_LED, HIGH);
}

void turnGreenLedOff(){
  digitalWrite(GREEN_LED, LOW);
}

void turnRelayOn(){
  digitalWrite(RELAY, HIGH);
  delay(500);
}

void turnRelayOff(){
  digitalWrite(RELAY, LOW);
  delay(500);
}


//////////////////////////////////////////////////////////////////////////////

// CHECK IF THE MAIN CONTAINER HAS A LOW AMOUNT OF WATER
int isMainContainerEmpty(){
  int mainSensorState = digitalRead(MAIN_CONTAINER_FLOAT);

  // // IF CONTAINER IS EMPTY
  if (mainSensorState == LOW) {
    return true;
  } 

  // IF CONTAINER IS NOT EMPTY
  else {
    return false;
  }

}

// CHECK IF THE BACKUP CONTAINER HAS A LOW AMOUNT OF WATER
int isBackupContainerEmpty(){
  int backupSensorState = digitalRead(BACKUP_CONTAINER_FLOAT);

  // // IF CONTAINER IS NOT EMPTY
  if (backupSensorState == LOW) {
    return true;
  } 

  // RETURN TRUE IF CONTAINER IS EMPTY
  else {
    return false;
  }
}

// DETECT THE WATER TEMPERATURE
float waterTemp(){
  
  sensors.requestTemperatures();
  float temperatureC = sensors.getTempCByIndex(0);

  return temperatureC;

  // delay(1500);
}

// AUTOMATIC THE MOTOR
void automaticallyRunMotor(){
  
  // CHECK IF MAIN CONTAINER IS EMPTY AND THE WATER TEMP IS HOT
  if ( isMainContainerEmpty() || waterTemp() > 32 ){

    turnRelayOn();

  }else{

    turnRelayOff();

  }

  // delay(3000);

}


//////////////////////////////////////////////////////////////////////////////

// SEND WATER TEMPERATURE
void sendWaterTemp(){

  // DETECT WATER TEMPERATURE
  float temperatureC = waterTemp();
  bool main_container_status = isMainContainerEmpty();
  bool back_container_status = isBackupContainerEmpty();

  if (temperatureC != DEVICE_DISCONNECTED_C){
    // JSON PAYLOAD
    String payload = "{\"temperature\":" + String(temperatureC, 2)+ "," + "\"main_container\":" + String(main_container_status) + "," + "\"backup_container\":" + String(back_container_status) + "}";

    // HEADER
    HTTPClient http;
    http.begin(client, device_status); 
    http.addHeader("Content-Type", "application/json");
    http.addHeader("Authorization", SECRET_KEY);

    int httpResponseCode = http.POST(payload);

    // CHECK WETHER SUCCESSFULL OR NOT
    if (httpResponseCode == 200) {
      turnGreenLedOn();
      delay(1000);
      turnGreenLedOff();
      Serial.println("Data sent successfully");
    }
    
    else {
      Serial.print("HTTP Error: ");
      Serial.println(httpResponseCode);
    }

    http.end();

    // SEND EVERY 60 SECS
    // delay(60000);
  }

  else {
    Serial.println("Error reading temperature data.");
  } 
    
}

//////////////////////////////////////////////////////////////////////////////

void setup(){

  // CONNECT TO WIFI
  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");

  Serial.begin(115200);

  // PRINT THE IP ADDRESS
  Serial.print("IP Address : ");
  Serial.println(WiFi.localIP());
  
  pinMode(GREEN_LED, OUTPUT);
  pinMode(RELAY, OUTPUT);
  pinMode(MAIN_CONTAINER_FLOAT, INPUT);
  pinMode(BACKUP_CONTAINER_FLOAT, INPUT);

  digitalWrite(GREEN_LED, LOW);
  digitalWrite(RELAY, LOW);
}

void loop(){
  sendWaterTemp();
  automaticallyRunMotor();
  delay(1000);
}