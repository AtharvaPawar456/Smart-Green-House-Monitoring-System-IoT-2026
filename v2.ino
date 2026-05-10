#include <WiFiNINA.h>
#include <Wire.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_TMP117.h>

// -------- WiFi Credentials --------
const char* wifiSsid = "Sahil's iPhone";
const char* wifiPassword = "12345678";

// -------- API Host --------
const char* apiHost = "sahilbaikar45.pythonanywhere.com";

WiFiClient wifiClient;

// -------- TMP117 ----------
Adafruit_TMP117 tmp11x;

// -------- Pins ------------
#define soilPin A0
#define rainPin 4

// -------- Sensor Variables ----------
float temp = 0.0;
float hum = 0.0;
int soilMoistureVal = 0;
int rain = 0;

/**
 * updateSensorValues()
 * -----------------------------------
 * Reads sensors and updates
 * global variables.
 */
void updateSensorValues() {

    // Wait until TMP117 data is ready
    while (!tmp11x.dataReady()) {
        delay(10);
    }

    // Read Temperature
    sensors_event_t tempEvent;
    tmp11x.getEvent(&tempEvent);

    temp = tempEvent.temperature;

    // Dummy Humidity Value
    hum = random(300, 900) / 10.0;

    // Read Soil Moisture
    soilMoistureVal = analogRead(soilPin);

    // Read Rain Sensor
    rain = digitalRead(rainPin);
}

/**
 * uploadDataApiCall()
 * -----------------------------------
 * Uploads sensor data to API server.
 */
void uploadDataApiCall() {

    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi disconnected!");
        return;
    }

    // Update Sensor Values
    updateSensorValues();

    // Create API URL
    String apiUrl =
        "/addlog?devicename=device123"
        "&tempval=" + String(temp, 1) +
        "&humval=" + String(hum, 1) +
        "&soilmoistureval=" + String(soilMoistureVal) +
        "&rainval=" + String(rain);

    Serial.println("Connecting to API...");

    if (wifiClient.connect(apiHost, 80)) {

        Serial.println("Connected to Server");

        // Send GET Request
        wifiClient.println("GET " + apiUrl + " HTTP/1.1");
        wifiClient.println("Host: " + String(apiHost));
        wifiClient.println("Connection: close");
        wifiClient.println();

        Serial.println("API Request Sent:");
        Serial.println(apiUrl);

        // Print Sensor Values
        Serial.println("\n------ Sensor Readings ------");

        Serial.print("Temperature: ");
        Serial.println(temp);

        Serial.print("Humidity: ");
        Serial.println(hum);

        Serial.print("Soil Moisture: ");
        Serial.println(soilMoistureVal);

        Serial.print("Rain Status: ");
        Serial.println(rain == HIGH ? "No Rain" : "Rain Detected");

        Serial.println("-----------------------------");

        // Read Server Response
        while (wifiClient.connected()) {
            while (wifiClient.available()) {
                char responseChar = wifiClient.read();
                Serial.print(responseChar);
            }
        }

        wifiClient.stop();

        Serial.println("\nConnection Closed");

    } else {
        Serial.println("Server Connection Failed!");
    }
}

void setup() {

    Serial.begin(115200);

    while (!Serial) {
        delay(10);
    }

    Serial.println("Starting System...");

    pinMode(rainPin, INPUT);

    // Initialize TMP117
    if (!tmp11x.begin()) {

        Serial.println("TMP117 Not Found!");

        while (1) {
            delay(10);
        }
    }

    Serial.println("TMP117 Ready");

    // Connect WiFi
    while (WiFi.begin(wifiSsid, wifiPassword) != WL_CONNECTED) {

        Serial.println("Connecting to WiFi...");
        delay(3000);
    }

    Serial.println("WiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());

    randomSeed(analogRead(A1));
}

void loop() {

    uploadDataApiCall();

    delay(10000);
}