// /*
//    AI-Thinker ESP32-CAM + PCA9685 + MQTT
//    – scans autonomously and listens for servo commands on topic `garden/servo`
//    – sends a JPEG to http://10.0.0.159:5000/upload every 10 s
// */
// #include <WiFi.h>
// #include <PubSubClient.h>
// #include <Wire.h>
// #include <Adafruit_PWMServoDriver.h>
// #include "esp_camera.h"

// // ---------- user settings ----------
// const char* WIFI_SSID   = "ivans";
// const char* WIFI_PASS   = "Solis656";
// const char* MQTT_HOST   = "10.0.0.159";   // broker runs beside FastAPI
// const int   MQTT_PORT   = 1883;
// const char* UPLOAD_URL  = "http://10.0.0.159:5000/upload";
// // ------------------------------------

// /***  PCA9685 wiring on free pins ***/
// #define I2C_SDA 13
// #define I2C_SCL 15
// Adafruit_PWMServoDriver pwm;
// #define SERVO_BASE   0    // yaw
// #define SERVO_PITCH  1    // pitch
// #define SERVOMIN 102
// #define SERVOMAX 512
// inline void setDeg(uint8_t ch, int deg) {
//   pwm.setPWM(ch, 0, map(deg, 0, 180, SERVOMIN, SERVOMAX));
// }

// /***  Wi-Fi + MQTT  ***/
// WiFiClient wifiClient;
// PubSubClient mqtt(wifiClient);

// void mqttCallback(char* topic, byte* payload, unsigned int len) {
//   /* Expected JSON: {"yaw":90,"pitch":45}                     */
//   StaticJsonDocument<64> doc;
//   DeserializationError err = deserializeJson(doc, payload, len);
//   if (!err) {
//     setDeg(SERVO_BASE,  doc["yaw"  ] | 0);
//     setDeg(SERVO_PITCH, doc["pitch"] | 0);
//   }
// }

// void mqttConnect() {
//   while (!mqtt.connected()) {
//     mqtt.connect("esp32cam");
//     if (mqtt.connected()) mqtt.subscribe("garden/servo");
//   }
// }

// /***  Camera task (FreeRTOS) ***/
// void cameraTask(void*) {
//   HTTPClient http;
//   for (;;) {
//     camera_fb_t* fb = esp_camera_fb_get();
//     if (fb) {
//       http.begin(UPLOAD_URL);
//       http.addHeader("Content-Type", "image/jpeg");
//       http.POST(fb->buf, fb->len);
//       http.end();
//       esp_camera_fb_return(fb);
//     }
//     vTaskDelay(pdMS_TO_TICKS(10'000));          // 10 s period
//   }
// }

// /***  Setup  ***/
// void setup() {
//   Serial.begin(115200);

//   /* Wi-Fi */
//   WiFi.begin(WIFI_SSID, WIFI_PASS);
//   while (WiFi.status() != WL_CONNECTED) delay(200);

//   /* MQTT */
//   mqtt.setServer(MQTT_HOST, MQTT_PORT);
//   mqtt.setCallback(mqttCallback);

//   /* I²C + servos */
//   Wire.begin(I2C_SDA, I2C_SCL, 400000);
//   pwm.begin();  pwm.setPWMFreq(50);
//   setDeg(SERVO_BASE,  90);   // centre on boot
//   setDeg(SERVO_PITCH, 45);

//   /* Camera (init exactly as in your working sketch) */
//   startCamera();             // ← use the function from your code

//   /* Kick off the camera upload task on core 1 */
//   xTaskCreatePinnedToCore(cameraTask, "cam", 8192, nullptr, 1, nullptr, 1);
// }

// void loop() {
//   if (!mqtt.connected()) mqttConnect();
//   mqtt.loop();                     // takes ~1 ms; keeps socket alive
//   vTaskDelay(pdMS_TO_TICKS(50));   // yield; nothing else to do
// }


/*
   ESP32-CAM + PCA9685
   – Moves two servos on boot
   – Captures and sends JPEG to http://10.0.0.159:5000/upload every 10 seconds
*/

#include <WiFi.h>
#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>
//#include <HttpClient.h>
#include "esp_camera.h"

// ---------- user settings ----------
const char* WIFI_SSID   = "ivans";
const char* WIFI_PASS   = "Solis656";
const char* UPLOAD_URL  = "http://10.0.0.159:5000/upload";
// ------------------------------------

// PCA9685 wiring
#define I2C_SDA 13
#define I2C_SCL 15
Adafruit_PWMServoDriver pwm;
#define SERVO_BASE   0    // yaw
#define SERVO_PITCH  1    // pitch
#define SERVOMIN 102
#define SERVOMAX 512

inline void setDeg(uint8_t ch, int deg) {
  pwm.setPWM(ch, 0, map(deg, 0, 180, SERVOMIN, SERVOMAX));
}

// Camera pin config (AI Thinker module)
camera_config_t camera_config = {
  .pin_pwdn  = 32,
  .pin_reset = -1,
  .pin_xclk = 0,
  .pin_sscb_sda = 26,
  .pin_sscb_scl = 27,

  .pin_d7 = 35,
  .pin_d6 = 34,
  .pin_d5 = 39,
  .pin_d4 = 36,
  .pin_d3 = 21,
  .pin_d2 = 19,
  .pin_d1 = 18,
  .pin_d0 = 5,
  .pin_vsync = 25,
  .pin_href = 23,
  .pin_pclk = 22,

  .xclk_freq_hz = 20000000,
  .ledc_timer = LEDC_TIMER_0,
  .ledc_channel = LEDC_CHANNEL_0,
  .pixel_format = PIXFORMAT_JPEG,
  .frame_size = FRAMESIZE_VGA,
  .jpeg_quality = 10,
  .fb_count = 1
};

void startCamera() {
  esp_err_t err = esp_camera_init(&camera_config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed: 0x%x", err);
    ESP.restart();
  }
}

/***  Image Upload Task  ***/
void cameraTask(void*) {
  for (;;) {
    camera_fb_t* fb = esp_camera_fb_get();
    if (fb) {
      HTTPClient http;
      http.begin(UPLOAD_URL);
      http.addHeader("Content-Type", "image/jpeg");
      int res = http.POST(fb->buf, fb->len);
      Serial.printf("Upload result: %d\n", res);
      http.end();
      esp_camera_fb_return(fb);
    }
    vTaskDelay(pdMS_TO_TICKS(10000)); // 10 seconds
  }
}

void setup() {
  Serial.begin(115200);

  // Wi-Fi connect
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  while (WiFi.status() != WL_CONNECTED) {
    Serial.print(".");
    delay(200);
  }
  Serial.println("\nWiFi connected");

  // I²C + servos
  Wire.begin(I2C_SDA, I2C_SCL, 400000);
  pwm.begin();
  pwm.setPWMFreq(50);
  setDeg(SERVO_BASE,  90);   // centre on boot
  setDeg(SERVO_PITCH, 45);

  // Camera setup
  startCamera();

  // Start image upload task
  xTaskCreatePinnedToCore(cameraTask, "cam", 8192, nullptr, 1, nullptr, 1);
}

void loop() {
  // Nothing to do here — cameraTask runs in parallel
  delay(100);
}
