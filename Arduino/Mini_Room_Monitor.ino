#include <DHT.h>
#include <LedControl.h>

// ====================================================
// MINI ROOM MONITOR
// Arduino UNO + DHT22 + MQ-135 + MAX7219 8x8 Matrix
// =====================================================

// =====================================================
// DHT22 TEMPERATURE & HUMIDITY SENSOR
// =====================================================

#define DHTPIN 4
#define DHTTYPE DHT22

DHT dht(DHTPIN, DHTTYPE);


// =====================================================
// MQ-135 GAS SENSOR
// =====================================================
//
// MQ-135 analog output -> Arduino A0
//
// The value reported by the Arduino is the raw ADC
// reading from 0 to 1023.
//
// It is NOT an AQI value and is NOT a direct ppm
// measurement for an individual gas.
// =====================================================

#define MQ135_PIN A0


// =====================================================
// MAX7219 8x8 LED DOT-MATRIX
// =====================================================
//
// MAX7219 DIN -> Arduino D11
// MAX7219 CLK -> Arduino D13
// MAX7219 CS  -> Arduino D10
//
// MAX7219 VCC -> 5V
// MAX7219 GND -> GND
// =====================================================

#define MATRIX_DIN 11
#define MATRIX_CLK 13
#define MATRIX_CS 10

LedControl matrix = LedControl(
  MATRIX_DIN,
  MATRIX_CLK,
  MATRIX_CS,
  1
);


// =====================================================
// TIMING
// =====================================================

unsigned long lastSensorRead = 0;
unsigned long lastDisplayChange = 0;

const unsigned long SENSOR_INTERVAL = 2000;
const unsigned long DISPLAY_INTERVAL = 2500;


// =====================================================
// SENSOR VALUES
// =====================================================

float temperature = NAN;
float humidity = NAN;

int mq135Raw = 0;


// =====================================================
// DISPLAY PAGE
// =====================================================
//
// 0 = Temperature
// 1 = Humidity
// 2 = MQ-135
// =====================================================

int displayPage = 0;


// =====================================================
// SETUP
// =====================================================

void setup() {

  Serial.begin(9600);

  // Start DHT22
  dht.begin();

  // Initialize MAX7219
  matrix.shutdown(0, false);

  // Brightness range: 0 to 15
  matrix.setIntensity(0, 5);

  matrix.clearDisplay(0);

  Serial.println();
  Serial.println("================================");
  Serial.println("      MINI ROOM MONITOR");
  Serial.println("================================");
  Serial.println("Arduino UNO");
  Serial.println("DHT22 + MQ-135 + MAX7219");
  Serial.println("Serial communication ready");
  Serial.println("================================");
  Serial.println();

  delay(1000);
}


// =====================================================
// READ SENSORS
// =====================================================

void readSensors() {

  // Read DHT22
  float newTemperature = dht.readTemperature();
  float newHumidity = dht.readHumidity();

  // Only update the stored value if the sensor
  // returned a valid reading.

  if (!isnan(newTemperature)) {

    temperature = newTemperature;

  }

  if (!isnan(newHumidity)) {

    humidity = newHumidity;

  }


  // Read raw MQ-135 analog value
  mq135Raw = analogRead(MQ135_PIN);
}


// =====================================================
// SEND SENSOR DATA AS JSON
// =====================================================
//
// The Python server reads these JSON messages from
// the Arduino USB serial connection.
//
// Example:
//
// {"temperature":27.4,"humidity":63.8,"mq135_raw":421}
//
// =====================================================

void sendSerialData() {

  Serial.print("{");

  // ---------------- TEMPERATURE ----------------

  Serial.print("\"temperature\":");

  if (isnan(temperature)) {

    Serial.print("null");

  } else {

    Serial.print(temperature, 1);

  }


  // ---------------- HUMIDITY ----------------

  Serial.print(",");

  Serial.print("\"humidity\":");

  if (isnan(humidity)) {

    Serial.print("null");

  } else {

    Serial.print(humidity, 1);

  }


  // ---------------- MQ-135 ----------------

  Serial.print(",");

  Serial.print("\"mq135_raw\":");

  Serial.print(mq135Raw);


  // ---------------- SENSOR NAME ----------------

  Serial.print(",");

  Serial.print("\"sensor\":\"MQ-135\"");


  Serial.println("}");
}


// =====================================================
// CLEAR MATRIX
// =====================================================

void clearMatrix() {

  matrix.clearDisplay(0);
}


// =====================================================
// DRAW TEMPERATURE LEVEL
// =====================================================
//
// The 8x8 matrix is used as a simple visual indicator.
// The actual numerical temperature is available on
// the web dashboard.
//
// 0°C -> 0 rows
// 40°C -> 8 rows
// =====================================================

void displayTemperature() {

  clearMatrix();

  int level = 0;

  if (!isnan(temperature)) {

    level = map(
      constrain((int)temperature, 0, 40),
      0,
      40,
      0,
      8
    );

  }


  for (int row = 0; row < level; row++) {

    for (int column = 0; column < 8; column++) {

      matrix.setLed(
        0,
        row,
        column,
        true
      );

    }

  }
}


// =====================================================
// DRAW HUMIDITY LEVEL
// =====================================================
//
// 0% -> 0 rows
// 100% -> 8 rows
// =====================================================

void displayHumidity() {

  clearMatrix();

  int level = 0;

  if (!isnan(humidity)) {

    level = map(
      constrain((int)humidity, 0, 100),
      0,
      100,
      0,
      8
    );

  }


  for (int row = 0; row < level; row++) {

    for (int column = 0; column < 8; column++) {

      matrix.setLed(
        0,
        row,
        column,
        true
      );

    }

  }
}


// =====================================================
// DRAW MQ-135 LEVEL
// =====================================================
//
// Raw ADC range:
// 0 -> 0 rows
// 1023 -> 8 rows
//
// This is only a visual representation of the raw
// sensor response and is NOT a gas concentration.
// =====================================================

void displayGas() {

  clearMatrix();

  int level = map(
    constrain(mq135Raw, 0, 1023),
    0,
    1023,
    0,
    8
  );


  for (int row = 0; row < level; row++) {

    for (int column = 0; column < 8; column++) {

      matrix.setLed(
        0,
        row,
        column,
        true
      );

    }

  }
}


// =====================================================
// UPDATE MATRIX DISPLAY
// =====================================================

void updateDisplay() {

  switch (displayPage) {

    case 0:

      displayTemperature();

      break;


    case 1:

      displayHumidity();

      break;


    case 2:

      displayGas();

      break;

  }


  displayPage++;


  if (displayPage > 2) {

    displayPage = 0;

  }
}


// =====================================================
// SERIAL DEBUG INFORMATION
// =====================================================

void printSensorDebug() {

  Serial.println();
  Serial.println("--- MINI ROOM MONITOR ---");


  // ---------------- TEMPERATURE ----------------

  Serial.print("Temperature: ");

  if (isnan(temperature)) {

    Serial.println("N/A");

  } else {

    Serial.print(temperature, 1);
    Serial.println(" °C");

  }


  // ---------------- HUMIDITY ----------------

  Serial.print("Humidity: ");

  if (isnan(humidity)) {

    Serial.println("N/A");

  } else {

    Serial.print(humidity, 1);
    Serial.println(" %");

  }


  // ---------------- MQ-135 ----------------

  Serial.print("MQ-135 Raw: ");
  Serial.println(mq135Raw);


  Serial.println("-------------------------");
}


// =====================================================
// MAIN LOOP
// =====================================================

void loop() {

  unsigned long currentMillis = millis();


  // =================================================
  // SENSOR UPDATE
  // =================================================

  if (
    currentMillis - lastSensorRead >=
    SENSOR_INTERVAL
  ) {

    lastSensorRead = currentMillis;

    readSensors();

    sendSerialData();

    printSensorDebug();

  }


  // =================================================
  // MATRIX DISPLAY UPDATE
  // =================================================

  if (
    currentMillis - lastDisplayChange >=
    DISPLAY_INTERVAL
  ) {

    lastDisplayChange = currentMillis;

    updateDisplay();

  }

}
