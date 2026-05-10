#include <WiFiNINA.h>

// WiFi Credentials
const char* wifiSsid = "Sahil's iPhone";
const char* wifiPassword = "12345678";

// API Host
const char* apiHost = "sahilbaikar45.pythonanywhere.com";

WiFiClient wifiClient;

// Sensor Variables
float temp = 0.0;
float hum = 0.0;
int soilMoistureVal = 0;
int rain = 0;

/**
 * uploadDataApiCall()
 * -----------------------------------
 * Connects to API server and uploads
 * sensor data using HTTP GET request.
 *
 * Inputs:
 *   Uses global variables
 *
 * Output:
 *   Prints server response on Serial
 */
void uploadDataApiCall() {
    if (WiFi.status() != WL_CONNECTED) {
        Serial.println("WiFi disconnected!");
        return;
    }

    // Generate Random Values
    temp = random(200, 400) / 10.0;          // 20.0 to 40.0
    hum = random(300, 900) / 10.0;           // 30.0 to 90.0
    soilMoistureVal = random(0, 1024);       // 0 to 1023
    rain = random(0, 2);                     // 0 or 1

    // Create URL
    String apiUrl =
        "/addlog?devicename=device123"
        "&tempval=" + String(temp, 1) +
        "&humval=" + String(hum, 1) +
        "&soilmoistureval=" + String(soilMoistureVal) +
        "&rainval=" + String(rain);

    Serial.println("Connecting to API...");

    if (wifiClient.connect(apiHost, 80)) {
        Serial.println("Connected to Server");

        // HTTP GET Request
        wifiClient.println("GET " + apiUrl + " HTTP/1.1");
        wifiClient.println("Host: " + String(apiHost));
        wifiClient.println("Connection: close");
        wifiClient.println();

        Serial.println("API Request Sent");
        Serial.println(apiUrl);

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

    while (!Serial);

    Serial.println("Starting WiFi Connection...");

    // Connect to WiFi
    while (WiFi.begin(wifiSsid, wifiPassword) != WL_CONNECTED) {
        Serial.println("Connecting to WiFi...");
        delay(3000);
    }

    Serial.println("WiFi Connected!");
    Serial.print("IP Address: ");
    Serial.println(WiFi.localIP());

    randomSeed(analogRead(A0));
}

void loop() {
    uploadDataApiCall();

    delay(10000); // Upload every 10 seconds
}