import os
import json
import time
import threading
from pathlib import Path

import serial
import serial.tools.list_ports

from flask import Flask, jsonify, request, send_from_directory
import requests


# =====================================================
# MINI ROOM MONITOR
# LOCAL WEB SERVER
# =====================================================

BASE_DIR = Path(__file__).resolve().parent.parent

WEB_DIR = BASE_DIR / "web"


# =====================================================
# FLASK APPLICATION
# =====================================================

app = Flask(
    __name__,
    static_folder=str(WEB_DIR),
    static_url_path=""
)


# =====================================================
# CONFIGURATION
# =====================================================

SERIAL_BAUD_RATE = 9600

SERIAL_PORT = os.getenv("ARDUINO_PORT", "")

OPENROUTER_API_KEY = os.getenv(
    "OPENROUTER_API_KEY",
    ""
)

OPENROUTER_MODEL = os.getenv(
    "OPENROUTER_MODEL",
    "google/gemma-3n-e2b-it:free"
)


# =====================================================
# SENSOR DATA
# =====================================================

latest_sensor_data = {
    "temperature": None,
    "humidity": None,
    "mq135_raw": None,
    "sensor": "MQ-135"
}


sensor_lock = threading.Lock()


# =====================================================
# SERIAL CONNECTION
# =====================================================

serial_connection = None


# =====================================================
# FIND ARDUINO
# =====================================================

def find_arduino_port():

    ports = list(
        serial.tools.list_ports.comports()
    )

    if not ports:

        print("No serial ports detected.")

        return None


    print()
    print("Available serial ports:")

    for port in ports:

        print(
            f"  {port.device} - "
            f"{port.description}"
        )


    # If the user explicitly configured a port,
    # use it.

    if SERIAL_PORT:

        print(
            f"Using configured Arduino port: "
            f"{SERIAL_PORT}"
        )

        return SERIAL_PORT


    # Try to automatically identify an Arduino.

    keywords = [
        "Arduino",
        "CH340",
        "USB-SERIAL",
        "USB Serial",
        "CP210",
        "FTDI"
    ]


    for port in ports:

        description = (
            port.description or ""
        ).lower()


        manufacturer = (
            port.manufacturer or ""
        ).lower()


        combined = (
            description +
            " " +
            manufacturer
        )


        for keyword in keywords:

            if keyword.lower() in combined:

                print(
                    f"Arduino detected on "
                    f"{port.device}"
                )

                return port.device


    # If automatic detection fails,
    # use the first available port.

    print(
        f"Using first available serial port: "
        f"{ports[0].device}"
    )

    return ports[0].device


# =====================================================
# CONNECT TO ARDUINO
# =====================================================

def connect_to_arduino():

    global serial_connection


    port = find_arduino_port()


    if port is None:

        return False


    try:

        serial_connection = serial.Serial(
            port,
            SERIAL_BAUD_RATE,
            timeout=1
        )


        # Give Arduino time to reset after
        # opening the serial port.

        time.sleep(2)


        print()
        print(
            f"Connected to Arduino on {port}"
        )
        print()


        return True


    except Exception as error:

        print(
            "Unable to connect to Arduino:"
        )

        print(error)

        serial_connection = None

        return False


# =====================================================
# SERIAL READER
# =====================================================

def serial_reader():

    global serial_connection


    while True:

        try:

            # If connection doesn't exist,
            # attempt to connect.

            if (
                serial_connection is None
                or
                not serial_connection.is_open
            ):

                connect_to_arduino()

                time.sleep(3)

                continue


            # Read one complete line.

            line = (
                serial_connection
                .readline()
                .decode(
                    "utf-8",
                    errors="ignore"
                )
                .strip()
            )


            if not line:

                continue


            # Arduino prints debug messages as well
            # as JSON. Only process JSON lines.

            if not line.startswith("{"):

                print(
                    "Arduino:",
                    line
                )

                continue


            try:

                data = json.loads(line)


            except json.JSONDecodeError:

                print(
                    "Invalid JSON from Arduino:",
                    line
                )

                continue


            # Update shared sensor data.

            with sensor_lock:

                if "temperature" in data:

                    latest_sensor_data[
                        "temperature"
                    ] = data["temperature"]


                if "humidity" in data:

                    latest_sensor_data[
                        "humidity"
                    ] = data["humidity"]


                if "mq135_raw" in data:

                    latest_sensor_data[
                        "mq135_raw"
                    ] = data["mq135_raw"]


                if "sensor" in data:

                    latest_sensor_data[
                        "sensor"
                    ] = data["sensor"]


        except (
            serial.SerialException,
            OSError
        ) as error:

            print(
                "Arduino serial connection lost:"
            )

            print(error)


            try:

                if serial_connection:

                    serial_connection.close()

            except Exception:

                pass


            serial_connection = None


            time.sleep(3)


        except Exception as error:

            print(
                "Serial reader error:",
                error
            )

            time.sleep(1)


# =====================================================
# GET CURRENT SENSOR DATA
# =====================================================

def get_sensor_data():

    with sensor_lock:

        return dict(
            latest_sensor_data
        )


# =====================================================
# GAS INFORMATION
# =====================================================

def get_mq135_information():

    return {

        "sensor": "MQ-135",

        "type": (
            "Broad-spectrum semiconductor "
            "gas sensor"
        ),

        "reading_type": (
            "Raw analog sensor value"
        ),

        "sensitive_to": [

            "Ammonia (NH3)",

            "Nitrogen oxides (NOx)",

            "Benzene-series vapors",

            "Smoke",

            "Sulfide gases"

        ]

    }


# =====================================================
# HOME PAGE
# =====================================================

@app.route("/")
def home():

    return send_from_directory(
        WEB_DIR,
        "index.html"
    )


# =====================================================
# SENSOR DATA ENDPOINT
# =====================================================

@app.route("/data")
def data_endpoint():

    data = get_sensor_data()


    gas_information = (
        get_mq135_information()
    )


    response = {

        "temperature":
            data["temperature"],

        "humidity":
            data["humidity"],

        "mq135_raw":
            data["mq135_raw"],

        "sensor":
            data["sensor"],

        "mq135_information":
            gas_information

    }


    return jsonify(response)


# =====================================================
# AI ENDPOINT
# =====================================================

@app.route(
    "/ai",
    methods=["POST"]
)
def ai_endpoint():

    if not OPENROUTER_API_KEY:

        return jsonify({

            "text": (
                "OpenRouter API key is not "
                "configured on the local server."
            )

        }), 500


    # Get latest sensor readings.

    sensor_data = get_sensor_data()


    temperature = (
        sensor_data["temperature"]
    )

    humidity = (
        sensor_data["humidity"]
    )

    mq135_raw = (
        sensor_data["mq135_raw"]
    )


    # Build a safe description of the MQ-135.

    gas_information = (
        "The MQ-135 is a broad-spectrum "
        "gas sensor sensitive to gases/vapors "
        "including ammonia (NH3), nitrogen "
        "oxides (NOx), benzene-series vapors, "
        "smoke and sulfide gases. The provided "
        "MQ-135 value is a raw analog sensor "
        "reading, not an AQI or calibrated ppm "
        "concentration."
    )


    prompt = f"""
You are an assistant for a small educational
room-monitoring project.

Current sensor readings:

Temperature: {temperature} °C
Humidity: {humidity} %
MQ-135 raw reading: {mq135_raw}

{gas_information}

Analyze the available readings conservatively.

Do not invent gas concentrations in ppm.
Do not calculate an AQI from the MQ-135 raw value.
Do not claim that a specific gas is present simply
because the MQ-135 is sensitive to it.

Give 2 or 3 short, practical suggestions about
the room environment based on the temperature,
humidity and the raw gas-sensor trend/value.

Clearly mention when a measurement cannot be
determined from the available sensors.
"""


    payload = {

        "model":
            OPENROUTER_MODEL,

        "messages": [

            {

                "role": "user",

                "content": prompt

            }

        ]

    }


    headers = {

        "Content-Type":
            "application/json",

        "Authorization":
            "Bearer " +
            OPENROUTER_API_KEY,

        "HTTP-Referer":
            "http://localhost:5000",

        "X-Title":
            "Mini Room Monitor"

    }


    try:

        response = requests.post(

            "https://openrouter.ai/api/v1/chat/completions",

            headers=headers,

            json=payload,

            timeout=30

        )


        if response.status_code != 200:

            print(
                "OpenRouter error:",
                response.status_code
            )

            print(
                response.text
            )


            return jsonify({

                "text":
                    "AI request failed. "
                    "Check the local server "
                    "console for details."

            }), 500


        result = response.json()


        choices = (
            result.get(
                "choices",
                []
            )
        )


        if not choices:

            return jsonify({

                "text":
                    "No AI response was returned."

            })


        message = (
            choices[0]
            .get("message", {})
        )


        text = (
            message
            .get(
                "content",
                "No AI response."
            )
        )


        return jsonify({

            "text": text

        })


    except requests.RequestException as error:

        print(
            "OpenRouter connection error:",
            error
        )


        return jsonify({

            "text":
                "Unable to connect to "
                "OpenRouter."

        }), 500


# =====================================================
# SERVER STARTUP
# =====================================================

def start_serial_thread():

    thread = threading.Thread(

        target=serial_reader,

        daemon=True

    )


    thread.start()


# =====================================================
# MAIN
# =====================================================

if __name__ == "__main__":

    print()
    print(
        "========================================"
    )

    print(
        "        MINI ROOM MONITOR"
    )

    print(
        "        Local Web Dashboard"
    )

    print(
        "========================================"
    )

    print()

    start_serial_thread()


    print(
        "Dashboard:"
    )

    print(
        "http://127.0.0.1:5000"
    )

    print()


    app.run(

        host="127.0.0.1",

        port=5000,

        debug=False,

        use_reloader=False

    )
