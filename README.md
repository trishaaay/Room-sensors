# Mini Room Monitor

A compact Arduino-based room monitoring system that measures temperature, humidity, and gas sensor readings and presents the information through both a physical LED matrix display and a local web dashboard.

The project combines an **Arduino UNO**, **DHT22 temperature and humidity sensor**, **MQ-135 gas sensor**, and **MAX7219 8×8 LED matrix display** to create a simple environmental monitoring prototype.

The sensor data can also be sent to a locally hosted custom web interface, where the readings are displayed in a more detailed and user-friendly format. An AI model accessed through **OpenRouter** can be connected to the local dashboard to interpret the collected readings and provide a human-readable summary of the current room conditions.

---

## Features

- Temperature monitoring using a DHT22 sensor
- Relative humidity monitoring using a DHT22 sensor
- MQ-135 gas sensor monitoring
- Displays raw gas sensor values instead of presenting an overall AQI
- Physical 8×8 LED matrix display using MAX7219
- Real-time sensor readings
- Serial communication between Arduino and the local computer
- JSON-formatted sensor data communication
- Local custom web dashboard
- Browser-based visualization of sensor readings
- AI-assisted interpretation of environmental readings
- OpenRouter API integration for the AI analysis layer
- Modular Arduino, server, and web components
- Low-cost and easily expandable hardware
- Designed as an educational environmental-monitoring and embedded-systems prototype

---

## Project Overview

The Mini Room Monitor is designed as a small-scale environmental monitoring system.

The Arduino continuously reads data from the connected sensors and provides the measurements to the rest of the system.

The physical hardware provides an immediate local indication of the readings through the LED matrix, while the computer-connected dashboard provides a more detailed interface.

The project is divided into three major parts:

1. **Arduino hardware and firmware**
2. **Local server / data processing layer**
3. **Web dashboard and AI analysis layer**

This separation keeps the sensor firmware simple while allowing the software side of the project to be expanded independently.

---

## Hardware

The prototype uses the following main components:

- Arduino UNO
- DHT22 temperature and humidity sensor
- MQ-135 gas sensor
- MAX7219 8×8 LED matrix display
- Breadboard
- Jumper wires
- USB cable
- Computer for the local dashboard and AI analysis

### Arduino UNO

The Arduino UNO acts as the main microcontroller.

It reads the connected sensors, processes the measurements, controls the MAX7219 LED matrix, and sends the sensor information over the USB serial connection.

The Arduino was selected because it is inexpensive, widely supported, and suitable for a simple sensor-monitoring prototype.

---

### DHT22 Temperature & Humidity Sensor

The DHT22 is used to measure:

- Temperature
- Relative humidity

The sensor provides digital readings to the Arduino.

Temperature and humidity are useful for basic room-environment monitoring and can also provide context when interpreting the gas sensor readings.

---

### MQ-135 Gas Sensor

The MQ-135 is used to monitor changes in the surrounding air/gas environment.

The sensor produces an analog output that is read by the Arduino's analog input.

The MQ-135 is commonly described as being sensitive to gases including:

- Ammonia (NH₃)
- Nitrogen oxides (NOx)
- Alcohol vapors
- Benzene
- Smoke
- Carbon dioxide (CO₂)

The sensor is a broad-response gas sensor rather than a laboratory-grade gas analyzer.

Therefore, the project displays the **sensor reading/value** instead of presenting the value as an exact concentration for each individual gas.

> **Important:** A raw MQ-135 analog value should not be interpreted as an exact ppm measurement for a particular gas without proper calibration and a suitable measurement model.

The dashboard therefore focuses on displaying the gas sensor reading and allowing the user to observe changes in the environment.

---

### MAX7219 8×8 LED Matrix

The MAX7219 LED matrix provides a small physical display for the project.

It can be used to show information such as:

- Temperature
- Humidity
- Gas sensor value
- Short status messages

The display provides a simple way to see the latest readings without opening the web dashboard.

---

## Hardware Prototype

<p align="center">
  <img src="docs/images/Hardware%20Front.jpg.jpeg" alt="Mini Room Monitor hardware front view" width="500">
</p>

The prototype is assembled on a breadboard using an Arduino UNO, DHT22, MQ-135, and MAX7219 LED matrix.

The wiring is kept exposed so that the individual components and connections can be easily inspected and modified.

<p align="center">
  <img src="docs/images/Model%20with%20a%20matrix%20display.jpg.jpeg" alt="Mini Room Monitor with matrix display" width="500">
</p>

---

## Physical Display

The LED matrix is intended to provide quick access to the latest measurements.

A typical display cycle can contain information such as:

```text
TEMP
26.4 C

HUM
58 %

GAS
412
```

The exact display sequence can be modified in the Arduino firmware.

The matrix is primarily intended as a compact local status display rather than a replacement for the detailed web dashboard.

---

# Software Architecture

The project consists of three main software layers.

```text
+--------------------------+
|       Arduino UNO        |
|                          |
|  DHT22     MQ-135        |
|    │          │          |
|    └────┬─────┘          |
|         │                |
|    Sensor Processing     |
|         │                |
|    MAX7219 Display       |
+---------┬----------------+
          │
          │ USB Serial
          │
          ▼
+--------------------------+
|     Local Server         |
|                          |
| Serial Data Processing   |
| JSON Data Handling       |
+------------┬-------------+
             │
             ▼
+--------------------------+
|     Web Dashboard        |
|                          |
| Temperature              |
| Humidity                 |
| Gas Sensor Value         |
| System Status            |
+------------┬-------------+
             │
             ▼
+--------------------------+
|      AI Analysis         |
|                          |
| OpenRouter API            |
| Environmental Reading    |
| Interpretation           |
+--------------------------+
```

---

# Arduino Firmware

The Arduino firmware is responsible for the hardware-side operation of the project.

Its main tasks are:

1. Initialize the sensors and display.
2. Read temperature from the DHT22.
3. Read humidity from the DHT22.
4. Read the analog value from the MQ-135.
5. Update the MAX7219 display.
6. Format the readings into structured data.
7. Send the data through the USB serial connection.

The Arduino does not require Wi-Fi for the current implementation.

Communication with the local dashboard is performed through the computer's serial connection.

---

# Sensor Data

The system currently provides three primary measurements.

### Temperature

Measured using:

```text
DHT22
```

Unit:

```text
°C
```

### Relative Humidity

Measured using:

```text
DHT22
```

Unit:

```text
%
```

### Gas Sensor Reading

Measured using:

```text
MQ-135
```

Output:

```text
Raw analog sensor value
```

The gas value is intentionally displayed as a sensor reading instead of being converted into a single AQI score.

This makes the current implementation more transparent because the MQ-135 is a broad-response sensor and requires calibration before its output can be reliably converted into gas-specific concentrations.

---

# Why the MQ-135 Value Is Not Presented as AQI

The project does not attempt to calculate an overall Air Quality Index from the MQ-135.

An AQI value normally requires pollutant-specific measurements and an appropriate conversion method.

The MQ-135 alone does not provide independent, calibrated concentrations for every gas it responds to.

Therefore, this project displays:

```text
Gas Sensor Value
```

instead of:

```text
AQI
```

This makes the dashboard more transparent about what the hardware is actually measuring.

The raw sensor value can still be useful for observing changes, such as an increase in the sensor response when exposed to smoke or other vapors.

---

# Serial Communication

The Arduino communicates with the local computer through USB serial communication.

A simplified data flow is:

```text
DHT22
  │
  ├── Temperature
  │
  └── Humidity
        │
        ▼
     Arduino
        │
MQ-135 ─┤
        │
        ▼
   JSON / Serial Data
        │
        ▼
   Local Computer
```

The local software reads the serial output and makes the latest sensor readings available to the web dashboard.

Structured data makes it easier for the server to process the Arduino output without relying on manually formatted text.

---

# Local Web Dashboard

The project also includes a custom locally hosted web dashboard.

The dashboard provides a more detailed interface than the physical LED matrix.

The dashboard can display:

- Temperature
- Humidity
- MQ-135 gas sensor value
- Current monitoring status
- AI-generated interpretation of the readings

The dashboard is designed to make the project easier to monitor from a computer browser.

---

## Dashboard

<p align="center">
  <img src="docs/images/Prototype%20Dashboard.jpg.jpeg" alt="Mini Room Monitor prototype web dashboard" width="700">
</p>

The dashboard provides a graphical representation of the sensor data received from the Arduino.

Instead of relying only on the small physical matrix, the browser interface allows multiple measurements and additional information to be presented at the same time.

---

# AI Analysis

One of the additional software features of the project is an AI-assisted interpretation layer.

The local dashboard can send the current sensor readings to an AI model through the **OpenRouter API**.

The AI receives the environmental measurements and can provide a human-readable interpretation of the current readings.

For example, instead of only showing:

```text
Temperature: 28.1 °C
Humidity: 63 %
Gas Sensor: 520
```

the AI layer can interpret the combination of readings and provide a simple explanation of what the current measurements may indicate.

The AI layer is intended for:

- Human-readable summaries
- Basic environmental interpretation
- Explaining changes in readings
- Making the dashboard easier to understand

It is not intended to replace calibrated environmental or medical-grade monitoring equipment.

---

# OpenRouter Integration

The AI component uses OpenRouter as the model-access layer.

The general flow is:

```text
Arduino Sensor Data
        ↓
Local Server
        ↓
Web Dashboard
        ↓
OpenRouter API
        ↓
AI Model
        ↓
Environmental Interpretation
        ↓
Web Dashboard
```

The API key should **never be hard-coded into the public GitHub repository**.

A private configuration method or environment variable should be used when configuring OpenRouter.

For example:

```text
OPENROUTER_API_KEY=your_key_here
```

Do not commit the real API key to GitHub.

If an API key is accidentally exposed, it should be revoked and replaced immediately.

---

# Privacy and Local Operation

The core sensor system is designed to work locally.

The Arduino itself does not require Wi-Fi for the current implementation.

The local computer acts as the bridge between the Arduino and the web dashboard.

The AI functionality is separate from the physical sensor system and requires an internet connection when communicating with the OpenRouter API.

Therefore:

```text
Sensors + Arduino
        ↓
      Local
        ↓
Web Dashboard
        ↓
OpenRouter
        ↓
     AI Model
```

The monitoring hardware itself remains simple and independent of cloud connectivity.

---

# How It Works

The complete system operates approximately as follows:

```text
Power on Arduino
       ↓
Initialize DHT22
       ↓
Initialize MQ-135
       ↓
Initialize MAX7219
       ↓
Read temperature
       ↓
Read humidity
       ↓
Read MQ-135 analog value
       ↓
Update LED matrix
       ↓
Format sensor data
       ↓
Send data through USB serial
       ↓
Local server receives data
       ↓
Dashboard updates
       ↓
Optional AI analysis
       ↓
AI interpretation displayed
```

---

# Data Flow

```text
              ┌──────────────┐
              │    DHT22     │
              │ Temp / Hum.  │
              └──────┬───────┘
                     │
                     │
              ┌──────▼───────┐
              │   Arduino    │
              │     UNO      │
              └──────┬───────┘
                     │
          ┌──────────┴──────────┐
          │                     │
          ▼                     ▼
    MAX7219 Matrix        USB Serial
          │                     │
          ▼                     ▼
   Physical Display       Local Server
                                │
                                ▼
                         Web Dashboard
                                │
                                ▼
                         OpenRouter API
                                │
                                ▼
                           AI Analysis
```

The MQ-135 connects directly to the Arduino and contributes its sensor reading to the same data pipeline.

---

# Project Structure

The project is organized into separate folders for the Arduino firmware, local server, web interface, and documentation.

```text
mini-room-monitor/
│
├── arduino/
│   └── Mini_Room_Monitor.ino
│
├── server/
│   └── ...
│
├── web/
│   └── ...
│
├── docs/
│   └── images/
│       ├── Hardware%20Front.jpg.jpeg.jpeg
│       ├── Model%20with%20a%20matrix%20display.jpg.jpeg.jpeg
│       ├── Model%20working%20taking%20readings.jpeg.jpeg.jpeg
│       └── Prototype%20Dashboard.jpg.jpeg.jpeg
│
├── LICENSE
└── README.md
```

The exact files inside the `server` and `web` directories may change as the project develops.

---

# Installation

## 1. Arduino Setup

Install the Arduino IDE and connect the Arduino UNO through USB.

Open:

```text
arduino/Mini_Room_Monitor.ino
```

Select:

```text
Board: Arduino UNO
```

Select the appropriate COM port.

Install the required Arduino libraries used by the firmware.

Upload the program to the Arduino.

---

## 2. Hardware Setup

Connect the components according to the pin definitions used in the Arduino firmware.

The main components are:

```text
Arduino UNO
    │
    ├── DHT22
    │
    ├── MQ-135
    │
    └── MAX7219 8×8 Matrix
```

Make sure the sensor power and ground connections are correct before powering the circuit.

---

## 3. Server Setup

The local server is responsible for receiving sensor information from the Arduino and making the data available to the web interface.

Enter the server directory:

```bash
cd server
```

Install the required dependencies according to the server implementation.

Configure the OpenRouter API key using a private configuration method or environment variable if AI functionality is enabled.

Then start the local server.

---

## 4. Open the Dashboard

After the server is running, open the local dashboard in a web browser.

The dashboard can then display the readings received from the Arduino.

---

# Requirements

## Hardware

- Arduino UNO
- DHT22
- MQ-135
- MAX7219 8×8 LED matrix
- Breadboard
- Jumper wires
- USB cable
- Computer

## Software

- Arduino IDE
- Arduino firmware
- Local server
- Modern web browser
- Internet connection for OpenRouter AI functionality

---

# Technologies Used

### Hardware

- **Arduino UNO**
- **DHT22**
- **MQ-135**
- **MAX7219**

### Firmware

- **Arduino C/C++**
- Arduino sensor libraries
- Serial communication

### Web

- **HTML**
- **CSS**
- **JavaScript**
- Local web server

### AI

- **OpenRouter API**
- Configurable AI model

---

# Design Goals

The project was designed around several simple goals.

### Low Cost

The system uses inexpensive and commonly available components.

### Easy to Understand

The hardware and software are intentionally kept relatively simple so that the complete system can be studied and modified.

### Expandability

The project is designed so that additional sensors and features can be added later.

### Local Monitoring

The Arduino and dashboard can operate locally without requiring a dedicated cloud IoT platform.

### Educational Use

The project demonstrates the interaction between:

```text
Sensors
   ↓
Microcontroller
   ↓
Serial Communication
   ↓
Server
   ↓
Web Interface
   ↓
AI
```

---

# Limitations

This project is a prototype and should not be considered a professional environmental monitoring instrument.

## MQ-135 Limitations

The MQ-135 is a broad-response gas sensor.

Its raw analog output is affected by factors such as:

- Sensor warm-up
- Temperature
- Humidity
- Sensor aging
- Supply voltage
- Environmental conditions
- Calibration
- Presence of multiple gases

Therefore, the gas reading in this project should primarily be treated as a relative sensor value.

It should not be interpreted as an accurate measurement of a specific gas concentration without proper calibration.

---

## DHT22 Limitations

The DHT22 is suitable for basic temperature and humidity monitoring but is not intended to replace professional environmental sensors.

Its readings can also be affected by:

- Sensor placement
- Airflow
- Heat sources
- Response time
- Environmental conditions

---

## LED Matrix Limitations

The 8×8 matrix has limited resolution and display space.

It is therefore mainly used for quick status information rather than detailed data visualization.

---

## AI Limitations

AI-generated interpretations are based on the sensor values provided to the model.

The AI does not make the underlying sensors more accurate.

For example:

```text
Better AI
≠
Better sensor accuracy
```

The quality of the AI interpretation depends on the quality and reliability of the underlying sensor data.

AI output should therefore be treated as an additional interpretation layer rather than a scientific measurement.

---

# Calibration

The current prototype focuses on displaying sensor readings rather than performing laboratory-grade calibration.

For meaningful gas concentration measurements, the MQ-135 would require an appropriate calibration procedure and a suitable conversion model.

Future versions can introduce:

- Baseline resistance measurement
- Sensor warm-up procedures
- Calibration against known reference conditions
- Gas-specific calibration curves
- Temperature and humidity compensation
- More accurate ADC processing

Similarly, temperature and humidity readings can be compared against a calibrated reference sensor to evaluate accuracy.

---

# Future Improvements

The project can be expanded significantly in future versions.

## Better Temperature and Humidity Sensor

The DHT22 can eventually be replaced with a more modern and accurate sensor such as:

- BME280
- SHT31
- SHTC3
- BME680

This could improve measurement stability and provide additional environmental information.

For example, the BME280 can provide:

```text
Temperature
Humidity
Pressure
```

---

## Better Particulate Matter Sensor

A dedicated particulate matter sensor would be a major improvement.

Possible future additions include:

- PMS5003
- PMS7003
- SDS011
- Other laser-based PM sensors

This would allow the project to measure particulate matter such as:

```text
PM1.0
PM2.5
PM10
```

A dedicated PM sensor would be much more appropriate for particulate monitoring than trying to infer particulate concentration from an MQ-135.

---

## Better Gas Sensor

The MQ-135 can eventually be supplemented or replaced with more specialized gas sensors.

Future versions could use sensors designed for specific gases or environmental conditions.

This could make the gas measurements more meaningful and allow calibrated concentration estimates.

---

## Buzzer / Alert System

A buzzer can be added to provide an audible warning when a configurable threshold is exceeded.

For example:

```text
Temperature too high
        ↓
     Buzzer
```

or:

```text
Gas sensor reading increased significantly
        ↓
      Warning
        ↓
      Buzzer
```

Thresholds should be configurable rather than permanently hard-coded.

---

## RGB Status LED

An RGB LED could provide a quick visual indication of system status.

For example:

```text
Green  → Normal
Yellow → Warning
Red    → Alert
```

This would complement the matrix display.

---

## Larger Display

The MAX7219 8×8 matrix could be replaced or supplemented with a larger display such as:

- OLED
- LCD
- TFT display

A larger display could show multiple measurements simultaneously.

---

## Historical Data

The local server could store sensor readings over time.

This would allow the dashboard to display graphs such as:

```text
Temperature vs Time
Humidity vs Time
Gas Sensor Value vs Time
```

This would make it possible to observe environmental trends instead of only viewing the current measurement.

---

## Data Logging

Future versions could save readings to:

```text
CSV
SQLite
JSON
```

This would allow sensor measurements to be analyzed later.

---

## Automatic Alerts

The dashboard could eventually provide configurable alerts.

For example:

```text
IF temperature > threshold
        ↓
Show warning
```

or:

```text
IF gas sensor value changes significantly
        ↓
Show warning
        ↓
Optional buzzer
```

---

## Improved AI Analysis

The AI component could eventually analyze historical measurements instead of only the latest readings.

For example:

```text
Current readings
       +
Historical readings
       ↓
AI Analysis
       ↓
Trend explanation
```

The AI could identify patterns such as gradual temperature increases or unusual changes in the gas sensor response.

---

## Mobile-Friendly Dashboard

The web interface can be improved for mobile devices so the monitoring system can be viewed from a phone or tablet connected to the same network.

---

## Wireless Connectivity

A future version could replace the USB serial connection with wireless communication using hardware such as:

- ESP32
- ESP8266
- Wi-Fi-enabled Arduino-compatible boards

This would allow the sensor unit to operate without being physically connected to the computer.

---

## Cloud / Remote Monitoring

Wireless connectivity could eventually allow the system to send readings to a remote server.

This could enable:

```text
Room
 ↓
Sensor Unit
 ↓
Wi-Fi
 ↓
Server
 ↓
Dashboard
```

Remote access should only be added after implementing appropriate authentication and security.

---

## Automatic Sensor Health Monitoring

A future version could monitor whether sensors are connected and responding correctly.

For example:

```text
DHT22 → Connected
MQ-135 → Connected
Display → Connected
```

This would make troubleshooting easier.

---

# Possible Future Hardware Architecture

A more advanced version could eventually look like:

```text
                 ┌──────────────┐
                 │ Temperature  │
                 │ + Humidity   │
                 └──────┬───────┘
                        │
 ┌──────────────┐       │
 │ PM2.5 Sensor ├───────┤
 └──────────────┘       │
                        ▼
                 ┌──────────────┐
                 │ Microcontrol │
                 │     ler      │
                 └──────┬───────┘
                        │
              ┌─────────┼─────────┐
              │         │         │
              ▼         ▼         ▼
           Display    Buzzer    Wi-Fi
                                  │
                                  ▼
                            Web Dashboard
                                  │
                                  ▼
                             AI Analysis
```

This would turn the current prototype into a much more complete room/environment monitoring platform.

---

# Educational Value

This project demonstrates several concepts in a single system:

- Microcontroller programming
- Sensor interfacing
- Analog and digital sensor readings
- Serial communication
- Embedded systems
- LED matrix control
- JSON-based data exchange
- Local server development
- Front-end web development
- API integration
- AI-assisted data interpretation
- Environmental monitoring
- Hardware/software integration

It can therefore serve as a practical example of how physical hardware can be connected to modern software and AI systems.

---

# Safety and Reliability

This project is intended for educational and experimental use.

The MQ-135 and other low-cost sensors should not be used as the sole basis for:

- Fire detection
- Toxic gas detection
- Medical decisions
- Industrial safety
- Emergency warnings
- Life-safety systems

For safety-critical applications, certified and properly calibrated sensors and monitoring equipment should be used.

---

# Development Philosophy

The project intentionally separates the physical sensing layer from the software and AI layers.

```text
Hardware Layer
      ↓
Sensor Readings
      ↓
Communication Layer
      ↓
Local Data Processing
      ↓
Visualization Layer
      ↓
Optional AI Interpretation
```

This makes it possible to improve one part of the project without completely redesigning the rest.

For example, the DHT22 could be replaced with a better temperature/humidity sensor without fundamentally changing the dashboard architecture.

---

# Project Status

**Prototype / Educational Project**

The current version demonstrates:

- Temperature monitoring
- Humidity monitoring
- MQ-135 gas sensor readings
- MAX7219 physical display
- Arduino-based sensor processing
- Serial data communication
- Local web dashboard
- Optional AI-powered interpretation through OpenRouter

The hardware and software architecture is intended to be expanded in future versions.

---

# Contributing

Contributions and improvements are welcome.

Possible areas for contribution include:

- Better sensor calibration
- Additional sensors
- Improved dashboard design
- Data logging
- Historical graphs
- Wireless connectivity
- Better error handling
- Mobile dashboard support
- Improved AI prompts
- Additional display options

If you build upon the project, documenting the hardware and software changes can make the project easier for others to reproduce.

---

# License

This project is licensed under the **MIT License**.

Copyright (c) 2026 Pannala Trishay Reddy  

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

See the `LICENSE` file in the repository for the full license text.

---

# Acknowledgements

This project uses commonly available open-source hardware and software components.

The project combines Arduino-based embedded development, sensor interfacing, web technologies, and AI API integration into a single experimental monitoring system.

---

# Summary

The **Mini Room Monitor** is a low-cost environmental monitoring prototype built around an Arduino UNO.

It combines:

```text
DHT22
   +
MQ-135
   +
MAX7219
   +
Arduino UNO
   +
Local Web Dashboard
   +
OpenRouter AI
```

The physical hardware provides real-time environmental readings, while the local dashboard provides a more detailed interface and optional AI-assisted interpretation.

The project is intentionally designed to be expandable, with future possibilities including dedicated PM2.5 monitoring, better temperature/humidity sensors, improved gas sensing, historical data logging, alerts, wireless connectivity, larger displays, and more advanced environmental analysis.
