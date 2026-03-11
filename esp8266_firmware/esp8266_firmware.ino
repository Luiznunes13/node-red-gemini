/**
 * ============================================================
 *  MCP Node-RED GPIO - Firmware ESP8266
 *  Ecossistema: Gemini CLI → main.py (MCP) → Node-RED → MQTT → ESP8266
 * ============================================================
 *
 *  Dependências (instalar no Arduino IDE / PlatformIO):
 *    - ESP8266WiFi        (incluso no core ESP8266)
 *    - PubSubClient       (Nick O'Leary) >= 2.8
 *    - ArduinoJson        >= 6.x
 *    - ArduinoOTA         (incluso no core ESP8266)
 *
 *  Tópicos MQTT subscritos:
 *    mcp/gpio/{pin}/set        → payload: "1"/"0" ou "on"/"off"
 *    mcp/gpio/all/set          → payload JSON: [{"pin":2,"state":"on"},...]
 *    mcp/device/{DEVICE_ID}/ota → payload: URL do firmware para OTA
 *
 *  Tópicos MQTT publicados:
 *    mcp/gpio/{pin}/status          → payload: "1" ou "0"
 *    mcp/device/{DEVICE_ID}/online  → payload: "1" (LWT: "0")
 *    mcp/device/{DEVICE_ID}/info    → payload JSON com info do device
 *    mcp/sensor/dht/temperature     → payload: "25.40" (°C)
 *    mcp/sensor/dht/humidity        → payload: "60.10" (%)
 *    mcp/sensor/dht/data            → payload JSON: {"temperature":25.4,"humidity":60.1}
 * ============================================================
 */

#include <ESP8266WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <ArduinoOTA.h>
#include <EEPROM.h>
#include <DHT.h>
#include "config.h"

// ============================================================
// CONSTANTES
// ============================================================
#define MQTT_RECONNECT_DELAY_MS  5000
#define WIFI_RECONNECT_DELAY_MS  10000
#define HEARTBEAT_INTERVAL_MS    30000
#define STATUS_PUBLISH_INTERVAL  60000
#define WATCHDOG_TIMEOUT_MS      8000

// GPIOs disponíveis no ESP8266 (BCM equivalente)
// D0=16, D1=5, D2=4, D3=0, D4=2, D5=14, D6=12, D7=13, D8=15
const uint8_t VALID_PINS[] = {2, 4, 5, 12, 13, 14, 16};
const uint8_t NUM_PINS = sizeof(VALID_PINS) / sizeof(VALID_PINS[0]);

// Estado atual dos GPIOs
uint8_t gpio_state[17] = {0};  // índice = número do pino

// ============================================================
// VARIÁVEIS GLOBAIS
// ============================================================
WiFiClient   wifiClient;
PubSubClient mqtt(wifiClient);
DHT          dht(DHT_PIN, DHT_TYPE);

unsigned long lastHeartbeat     = 0;
unsigned long lastStatusPublish = 0;
unsigned long lastWifiCheck     = 0;
unsigned long lastMqttCheck     = 0;
unsigned long lastDhtRead       = 0;

char deviceTopic[64];
char onlineTopic[64];
char infoTopic[64];

// ============================================================
// PROTÓTIPOS
// ============================================================
void setupWiFi();
void setupMQTT();
void setupOTA();
void setupGPIOs();
void reconnectMQTT();
void onMqttMessage(char* topic, byte* payload, unsigned int length);
void setGPIO(uint8_t pin, bool state);
bool isValidPin(uint8_t pin);
bool parseState(const String& value);
void publishGPIOStatus(uint8_t pin);
void publishAllStatus();
void publishDeviceInfo();
void publishDHTData();
void sendHeartbeat();
void handleWatchdog();

// ============================================================
// SETUP
// ============================================================
void setup() {
  Serial.begin(115200);
  delay(200);

  Serial.println(F("\n========================================"));
  Serial.println(F("  MCP Node-RED GPIO - ESP8266 Firmware"));
  Serial.println(F("========================================"));
  Serial.printf("  Device ID : %s\n", DEVICE_ID);
  Serial.printf("  Version   : %s\n", FIRMWARE_VERSION);
  Serial.println(F("========================================\n"));

  // Montar tópicos com device ID
  snprintf(deviceTopic, sizeof(deviceTopic), "mcp/device/%s", DEVICE_ID);
  snprintf(onlineTopic,  sizeof(onlineTopic),  "mcp/device/%s/online", DEVICE_ID);
  snprintf(infoTopic,    sizeof(infoTopic),    "mcp/device/%s/info",   DEVICE_ID);

  setupGPIOs();
  dht.begin();
  Serial.printf("[DHT] Sensor iniciado no pino %d\n", DHT_PIN);

  // Blink de boot no LED (D5/GPIO14) para confirmar que gravou
  for (uint8_t i = 0; i < 3; i++) {
#ifdef GPIO_ACTIVE_LOW
    digitalWrite(LED_PIN, LOW);  delay(150);  // active-low: LOW acende
    digitalWrite(LED_PIN, HIGH); delay(150);
#else
    digitalWrite(LED_PIN, HIGH); delay(150);
    digitalWrite(LED_PIN, LOW);  delay(150);
#endif
  }

  setupWiFi();

  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setCallback(onMqttMessage);
  mqtt.setBufferSize(512);

  setupOTA();

  Serial.println(F("Setup concluído. Entrando no loop principal.\n"));
}

// ============================================================
// LOOP PRINCIPAL
// ============================================================
void loop() {
  ArduinoOTA.handle();
  handleWatchdog();

  // Garantir conexão WiFi
  if (WiFi.status() != WL_CONNECTED) {
    if (millis() - lastWifiCheck > WIFI_RECONNECT_DELAY_MS) {
      lastWifiCheck = millis();
      Serial.println(F("[WiFi] Reconectando..."));
      WiFi.reconnect();
    }
    return;
  }

  // Garantir conexão MQTT
  if (!mqtt.connected()) {
    if (millis() - lastMqttCheck > MQTT_RECONNECT_DELAY_MS) {
      lastMqttCheck = millis();
      reconnectMQTT();
    }
    return;
  }

  mqtt.loop();

  // Heartbeat periódico
  if (millis() - lastHeartbeat > HEARTBEAT_INTERVAL_MS) {
    lastHeartbeat = millis();
    sendHeartbeat();
  }

  // Publicar status completo periodicamente
  if (millis() - lastStatusPublish > STATUS_PUBLISH_INTERVAL) {
    lastStatusPublish = millis();
    publishAllStatus();
  }

  // Leitura e publicação do DHT
  if (millis() - lastDhtRead > DHT_INTERVAL_MS) {
    lastDhtRead = millis();
    publishDHTData();
  }
}

// ============================================================
// WIFI
// ============================================================
void setupWiFi() {
  Serial.printf("[WiFi] Conectando em '%s'", WIFI_SSID);

  WiFi.mode(WIFI_STA);
  WiFi.hostname(DEVICE_ID);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  uint8_t attempts = 0;
  while (WiFi.status() != WL_CONNECTED && attempts < 30) {
    delay(500);
    Serial.print(F("."));
    attempts++;
  }

  if (WiFi.status() == WL_CONNECTED) {
    Serial.printf("\n[WiFi] Conectado! IP: %s\n", WiFi.localIP().toString().c_str());
  } else {
    Serial.println(F("\n[WiFi] Falha na conexão. Continuando sem WiFi..."));
  }
}

// ============================================================
// MQTT - RECONEXÃO
// ============================================================
void reconnectMQTT() {
  Serial.printf("[MQTT] Conectando em %s:%d como '%s'...\n", MQTT_HOST, MQTT_PORT, DEVICE_ID);

  bool connected = false;

#if defined(MQTT_USER) && defined(MQTT_PASSWORD)
  connected = mqtt.connect(DEVICE_ID, MQTT_USER, MQTT_PASSWORD, onlineTopic, 1, true, "0");
#else
  connected = mqtt.connect(DEVICE_ID, nullptr, nullptr, onlineTopic, 1, true, "0");
#endif

  if (connected) {
    Serial.println(F("[MQTT] Conectado!"));

    // Publicar online
    mqtt.publish(onlineTopic, "1", true);

    // Subscrever tópicos de controle
    char subTopic[64];

    // Controle individual: mcp/gpio/+/set
    snprintf(subTopic, sizeof(subTopic), "mcp/gpio/+/set");
    mqtt.subscribe(subTopic, 1);
    Serial.printf("[MQTT] Subscrito: %s\n", subTopic);

    // Controle em massa: mcp/gpio/all/set
    snprintf(subTopic, sizeof(subTopic), "mcp/gpio/all/set");
    mqtt.subscribe(subTopic, 1);
    Serial.printf("[MQTT] Subscrito: %s\n", subTopic);

    // OTA via MQTT: mcp/device/{id}/ota
    snprintf(subTopic, sizeof(subTopic), "mcp/device/%s/ota", DEVICE_ID);
    mqtt.subscribe(subTopic, 1);
    Serial.printf("[MQTT] Subscrito: %s\n", subTopic);

    // Publicar info do device
    publishDeviceInfo();
    publishAllStatus();

  } else {
    Serial.printf("[MQTT] Falha. Código: %d. Tentando novamente em %d ms\n",
                  mqtt.state(), MQTT_RECONNECT_DELAY_MS);
  }
}

// ============================================================
// CALLBACK MQTT - RECEBE MENSAGENS
// ============================================================
void onMqttMessage(char* topic, byte* payload, unsigned int length) {
  // Garantir null-terminator seguro
  char msg[256];
  length = min(length, (unsigned int)(sizeof(msg) - 1));
  memcpy(msg, payload, length);
  msg[length] = '\0';

  String topicStr(topic);
  String msgStr(msg);
  msgStr.trim();

  Serial.printf("[MQTT] Recebido [%s]: %s\n", topic, msg);

  // ── Controle individual: mcp/gpio/{pin}/set ──────────────
  if (topicStr.startsWith("mcp/gpio/") && topicStr.endsWith("/set")) {
    String pinPart = topicStr.substring(9, topicStr.length() - 4);

    // Ignorar tópico "all/set" que cai aqui por causa do wildcard
    if (pinPart == "all") return;

    uint8_t pin = (uint8_t)pinPart.toInt();
    if (!isValidPin(pin)) {
      Serial.printf("[GPIO] Pino %d inválido para este device.\n", pin);
      return;
    }

    bool state = parseState(msgStr);
    setGPIO(pin, state);
    publishGPIOStatus(pin);
    return;
  }

  // ── Controle em massa: mcp/gpio/all/set ──────────────────
  if (topicStr == "mcp/gpio/all/set") {
    StaticJsonDocument<256> doc;
    DeserializationError err = deserializeJson(doc, msg);

    if (err) {
      Serial.printf("[JSON] Erro ao parsear: %s\n", err.c_str());
      return;
    }

    if (doc.is<JsonArray>()) {
      JsonArray arr = doc.as<JsonArray>();
      for (JsonObject item : arr) {
        uint8_t pin   = item["pin"]   | 255;
        const char* st = item["state"] | "off";
        if (pin == 255 || !isValidPin(pin)) continue;
        bool state = parseState(String(st));
        setGPIO(pin, state);
        publishGPIOStatus(pin);
      }
    }
    return;
  }

  // ── OTA via MQTT (reservado para futuro) ─────────────────
  char otaTopic[64];
  snprintf(otaTopic, sizeof(otaTopic), "mcp/device/%s/ota", DEVICE_ID);
  if (topicStr == otaTopic) {
    Serial.printf("[OTA] Solicitação recebida. URL: %s\n", msg);
    // Implementação de HTTP OTA pode ser adicionada aqui
    // com ESP8266httpUpdate
  }
}

// ============================================================
// GPIO
// ============================================================
void setupGPIOs() {
  for (uint8_t i = 0; i < NUM_PINS; i++) {
    uint8_t pin = VALID_PINS[i];
    pinMode(pin, OUTPUT);
#ifdef GPIO_ACTIVE_LOW
    digitalWrite(pin, HIGH);  // active-low: HIGH = desligado no boot
#else
    digitalWrite(pin, LOW);
#endif
    gpio_state[pin] = 0;
    Serial.printf("[GPIO] Pino %d configurado como OUTPUT (OFF)\n", pin);
  }
}

void setGPIO(uint8_t pin, bool state) {
  gpio_state[pin] = state ? 1 : 0;
#ifdef GPIO_ACTIVE_LOW
  digitalWrite(pin, state ? LOW : HIGH);  // lógica invertida: ON=LOW, OFF=HIGH
#else
  digitalWrite(pin, state ? HIGH : LOW);
#endif
  Serial.printf("[GPIO] Pino %d → %s\n", pin, state ? "ON" : "OFF");
}

bool isValidPin(uint8_t pin) {
  for (uint8_t i = 0; i < NUM_PINS; i++) {
    if (VALID_PINS[i] == pin) return true;
  }
  return false;
}

bool parseState(const String& value) {
  String v = value;
  v.toLowerCase();
  return (v == "1" || v == "on" || v == "true" || v == "high");
}

// ============================================================
// PUBLICAÇÕES MQTT
// ============================================================
void publishGPIOStatus(uint8_t pin) {
  char topic[64];
  snprintf(topic, sizeof(topic), "mcp/gpio/%d/status", pin);
  char payload[2] = { (char)('0' + gpio_state[pin]), '\0' };
  mqtt.publish(topic, payload, true);  // retain=true
}

void publishAllStatus() {
  Serial.println(F("[MQTT] Publicando status de todos os pinos..."));
  for (uint8_t i = 0; i < NUM_PINS; i++) {
    publishGPIOStatus(VALID_PINS[i]);
    delay(20);  // evitar flood no broker
  }
}

void publishDeviceInfo() {
  StaticJsonDocument<256> doc;
  doc["device_id"]  = DEVICE_ID;
  doc["firmware"]   = FIRMWARE_VERSION;
  doc["ip"]         = WiFi.localIP().toString();
  doc["rssi"]       = WiFi.RSSI();
  doc["chip_id"]    = String(ESP.getChipId(), HEX);
  doc["free_heap"]  = ESP.getFreeHeap();
  doc["num_pins"]   = NUM_PINS;

  char buf[256];
  serializeJson(doc, buf, sizeof(buf));
  mqtt.publish(infoTopic, buf, true);
  Serial.printf("[MQTT] Info publicada: %s\n", buf);
}

void publishDHTData() {
  float temp = dht.readTemperature();
  float hum  = dht.readHumidity();

  if (isnan(temp) || isnan(hum)) {
    Serial.println(F("[DHT] Falha na leitura do sensor!"));
    return;
  }

  // Publicar individualmente
  char buf[16];
  snprintf(buf, sizeof(buf), "%.1f", temp);
  mqtt.publish("mcp/sensor/dht/temperature", buf, true);

  snprintf(buf, sizeof(buf), "%.1f", hum);
  mqtt.publish("mcp/sensor/dht/humidity", buf, true);

  // Publicar JSON consolidado
  StaticJsonDocument<128> doc;
  doc["temperature"] = temp;
  doc["humidity"]    = hum;
  doc["device_id"]   = DEVICE_ID;
  doc["timestamp"]   = millis();
  char json[128];
  serializeJson(doc, json, sizeof(json));
  mqtt.publish("mcp/sensor/dht/data", json, true);

  Serial.printf("[DHT] Temp: %.1f°C  Umidade: %.1f%%\n", temp, hum);
}

void sendHeartbeat() {
  mqtt.publish(onlineTopic, "1", true);

  // Publicar RSSI para monitoramento de sinal
  char rssiBuf[8];
  snprintf(rssiBuf, sizeof(rssiBuf), "%d", WiFi.RSSI());
  char rssiTopic[64];
  snprintf(rssiTopic, sizeof(rssiTopic), "mcp/device/%s/rssi", DEVICE_ID);
  mqtt.publish(rssiTopic, rssiBuf);
}

// ============================================================
// OTA (Over-The-Air Update)
// ============================================================
void setupOTA() {
  ArduinoOTA.setHostname(DEVICE_ID);

#ifdef OTA_PASSWORD
  ArduinoOTA.setPassword(OTA_PASSWORD);
#endif

  ArduinoOTA.onStart([]() {
    Serial.println(F("[OTA] Iniciando atualização..."));
  });

  ArduinoOTA.onEnd([]() {
    Serial.println(F("\n[OTA] Atualização concluída! Reiniciando..."));
  });

  ArduinoOTA.onProgress([](unsigned int progress, unsigned int total) {
    Serial.printf("[OTA] Progresso: %u%%\r", (progress / (total / 100)));
  });

  ArduinoOTA.onError([](ota_error_t error) {
    Serial.printf("[OTA] Erro [%u]: ", error);
    if      (error == OTA_AUTH_ERROR)    Serial.println(F("Autenticação falhou"));
    else if (error == OTA_BEGIN_ERROR)   Serial.println(F("Falha ao iniciar"));
    else if (error == OTA_CONNECT_ERROR) Serial.println(F("Falha de conexão"));
    else if (error == OTA_RECEIVE_ERROR) Serial.println(F("Falha ao receber"));
    else if (error == OTA_END_ERROR)     Serial.println(F("Falha ao finalizar"));
  });

  ArduinoOTA.begin();
  Serial.println(F("[OTA] Pronto para atualizações OTA"));
}

// ============================================================
// WATCHDOG DE SOFTWARE
// ============================================================
void handleWatchdog() {
  ESP.wdtFeed();  // Resetar watchdog de hardware do ESP8266
}
