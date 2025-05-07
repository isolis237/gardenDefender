// This script sends periodic images to server
#include <Arduino.h>
#include "esp_camera.h"
#include <WiFi.h>
#include <HTTPClient.h>

// ---------------------
// Update with your info
// ---------------------
const char* ssid       = "ivans";
const char* password   = "Solis656";
const char* serverUrl  = "http://10.0.0.159:5000/upload";

// Pin definition for AI Thinker ESP32-CAM
#define PWDN_GPIO_NUM    32
#define RESET_GPIO_NUM   -1
#define XCLK_GPIO_NUM     0
#define SIOD_GPIO_NUM    26
#define SIOC_GPIO_NUM    27
#define Y9_GPIO_NUM      35
#define Y8_GPIO_NUM      34
#define Y7_GPIO_NUM      39
#define Y6_GPIO_NUM      36
#define Y5_GPIO_NUM      21
#define Y4_GPIO_NUM      19
#define Y3_GPIO_NUM      18
#define Y2_GPIO_NUM       5
#define VSYNC_GPIO_NUM   25
#define HREF_GPIO_NUM    23
#define PCLK_GPIO_NUM    22

const int ledPin = 4;
const int freq = 5000;
const uint8_t pwmResolution = 8;

//---------------------------------------------------------
void startCamera() {
  Serial.println("[INFO] Initializing camera...");
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer   = LEDC_TIMER_0;
  config.pin_d0       = Y2_GPIO_NUM;
  config.pin_d1       = Y3_GPIO_NUM;
  config.pin_d2       = Y4_GPIO_NUM;
  config.pin_d3       = Y5_GPIO_NUM;
  config.pin_d4       = Y6_GPIO_NUM;
  config.pin_d5       = Y7_GPIO_NUM;
  config.pin_d6       = Y8_GPIO_NUM;
  config.pin_d7       = Y9_GPIO_NUM;
  config.pin_xclk     = XCLK_GPIO_NUM;
  config.pin_pclk     = PCLK_GPIO_NUM;
  config.pin_vsync    = VSYNC_GPIO_NUM;
  config.pin_href     = HREF_GPIO_NUM;
  config.pin_sscb_sda = SIOD_GPIO_NUM;
  config.pin_sscb_scl = SIOC_GPIO_NUM;
  config.pin_pwdn     = PWDN_GPIO_NUM;
  config.pin_reset    = RESET_GPIO_NUM;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  config.frame_size   = FRAMESIZE_VGA;
  config.jpeg_quality = 12;
  config.fb_count     = 1;

  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("[ERROR] Camera init failed: 0x%x\n", err);
  } else {
    Serial.println("[INFO] Camera initialized successfully.");
  }
}

//---------------------------------------------------------
void setup() {
  Serial.begin(115200);
  delay(200);

  Serial.println("[BOOT] ESP32-CAM Starting...");

  // Attach PWM
  ledcAttach(ledPin, freq, pwmResolution);

  // Connect to WiFi
  Serial.printf("[INFO] Connecting to WiFi: %s\n", ssid);
  WiFi.begin(ssid, password);
  int attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 20) {
    delay(500);
    Serial.print(".");
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.println("\n[INFO] WiFi connected!");
    Serial.print("[INFO] IP Address: ");
    Serial.println(WiFi.localIP());
  } else {
    Serial.println("\n[ERROR] WiFi connection failed!");
  }

  startCamera();
}

//---------------------------------------------------------
void loop() {
  Serial.println("[INFO] Capturing image...");

  // Turn on LED
  ledcWrite(ledPin, 120);
  delay(100);

  // Capture
  camera_fb_t* fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("[ERROR] Camera capture failed");
    ledcWrite(ledPin, 0);
    delay(5000);
    return;
  }

  Serial.printf("[INFO] Image captured: %d bytes\n", fb->len);
  ledcWrite(ledPin, 0);  // Turn off LED

  // Send HTTP POST
  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("[INFO] Sending image to server: %s\n", serverUrl);
    HTTPClient http;
    http.begin(serverUrl);
    http.addHeader("Content-Type", "image/jpeg");
    int httpResponseCode = http.POST(fb->buf, fb->len);

    if (httpResponseCode > 0) {
      String response = http.getString();
      Serial.printf("[SUCCESS] HTTP %d: %s\n", httpResponseCode, response.c_str());
    } else {
      Serial.printf("[ERROR] HTTP POST failed: %s\n", http.errorToString(httpResponseCode).c_str());
    }

    http.end();
  } else {
    Serial.println("[ERROR] WiFi not connected, skipping upload");
  }

  esp_camera_fb_return(fb);
  delay(10000);
}
