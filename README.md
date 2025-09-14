# PiBoy

A retro gaming and utility device powered by a Raspberry Pi Zero 2 W and a 0.96" I2C OLED display.

## Hardware

This section covers all the hardware-related aspects of the project.

### Hardware Requirements

*   Raspberry Pi Zero 2 W
*   0.96" I2C 4-pin OLED display (128x64)
*   Micro SD card (8GB or larger)
*   Power supply
*   Buttons for input
*   (Optional) Bluetooth speaker
*   (Optional) Wi-Fi dongle

### Hardware Setup

#### I2C OLED Display

Connect the I2C OLED display to the Raspberry Pi's GPIO pins:
*   VCC to a 3.3V pin
*   GND to a GND pin
*   SCL to GPIO 3 (SCL)
*   SDA to GPIO 2 (SDA)

#### Button Matrix Keypad

This project uses an 8-button matrix keypad for user input. The keypad is arranged in a 4x2 matrix, which allows us to use only 6 GPIO pins to read 8 buttons.

##### Wiring Diagram

Here is the wiring diagram for the 4x2 button matrix:

![Button Matrix](button4x2.svg)

##### How it Works

The button matrix is organized into rows and columns. In this 4x2 matrix, we have 4 rows (R1, R2, R3, R4) and 2 columns (C1, C2). Each button is located at the intersection of a row and a column.

To detect a button press, we will:
1.  Set all row pins to a high state.
2.  Set all column pins as inputs with a pull-down resistor.
3.  Iterate through each row, setting the current row pin to a low state.
4.  Check the state of each column pin. If a column pin is low, it means the button at the intersection of the current row and that column is pressed.

##### GPIO Connections

Connect the rows and columns to the Raspberry Pi's GPIO pins as follows:

*   **R1:** GPIO 5
*   **R2:** GPIO 6
*   **R3:** GPIO 13
*   **R4:** GPIO 19
*   **C1:** GPIO 26
*   **C2:** GPIO 21

## Software

This section covers all the software-related aspects of the project.

### Software Requirements

*   Raspberry Pi OS (Legacy)
*   Python 3
*   Git

### Python Libraries

*   `adafruit-circuitpython-ssd1306`
*   `Pillow`
*   `smbus`
*   `RPI.GPIO`

### Installation

1.  **Flash Raspberry Pi OS:**
    *   Download the Raspberry Pi Imager.
    *   Choose "Raspberry Pi OS (Legacy)" and write it to your micro SD card.
    *   Enable SSH and configure Wi-Fi by creating a `ssh` file and a `wpa_supplicant.conf` file in the boot partition of the SD card.

2.  **Software Setup:**
    *   Boot up your Raspberry Pi and connect to it via SSH.
    *   Update the package list:
        ```bash
        sudo apt-get update
        ```
    *   Install the required system libraries:
        ```bash
        sudo apt-get install -y python3-pip python3-pil i2c-tools
        ```
    *   Enable I2C:
        *   Run `sudo raspi-config`.
        *   Go to "Interfacing Options" -> "I2C".
        *   Enable the I2C interface.
        *   Reboot the Raspberry Pi.
    *   Verify that the display is detected:
        ```bash
        i2cdetect -y 1
        ```
        You should see a device at address `0x3C`.
    *   Install the required Python libraries:
        ```bash
        pip3 install adafruit-circuitpython-ssd1306 Pillow smbus RPi.GPIO
        ```

3.  **Clone the Repository:**
    ```bash
    git clone <repository-url>
    cd piboy
    ```

### Usage

Run the main script with Python 3:

```bash
python3 piboy_main.py
```

### Button Matrix Code

Here is a Python code snippet to read the button presses from the matrix:

```python
import RPi.GPIO as GPIO
import time

# GPIO setup
GPIO.setmode(GPIO.BCM)

# Row pins
rows = [5, 6, 13, 19]
# Column pins
cols = [26, 21]

# Button mapping
buttons = [
    ["A", "B"],
    ["S", "SE"],
    ["ST", "A"],
    ["W", "D"]
]

# Setup row pins as outputs
for row_pin in rows:
    GPIO.setup(row_pin, GPIO.OUT)
    GPIO.output(row_pin, GPIO.HIGH)

# Setup column pins as inputs with pull-down resistors
for col_pin in cols:
    GPIO.setup(col_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

def get_button_press():
    for i, row_pin in enumerate(rows):
        GPIO.output(row_pin, GPIO.LOW)
        for j, col_pin in enumerate(cols):
            if GPIO.input(col_pin) == GPIO.LOW:
                GPIO.output(row_pin, GPIO.HIGH)
                return buttons[i][j]
        GPIO.output(row_pin, GPIO.HIGH)
    return None

try:
    while True:
        button = get_button_press()
        if button:
            print(f"Button pressed: {button}")
        time.sleep(0.1)

except KeyboardInterrupt:
    GPIO.cleanup()
```

### Modes

The PiBoy has several modes:

*   **Game:** Play classic retro games.
*   **Music:** Connect to a Bluetooth speaker and play music.
*   **Stats:** Display system statistics like CPU usage, temperature, and memory.
*   **Terminal:** A mini terminal interface.
*   **Wi-Fi:** Manage Wi-Fi connections.
*   **Bluetooth:** Manage Bluetooth devices.

### Games

The following games are included:

*   **Breakout:** A classic arcade game where you break bricks with a ball and paddle.
*   **Frogger:** Help a frog cross a busy road and a treacherous river.
*   **Invaders:** Defend the Earth from waves of descending aliens.
*   **Pong:** The original table tennis-like arcade game.
*   **Snake:** Control a growing snake to eat food and avoid crashing into itself.
*   **Tetris:** Fit falling blocks together to clear lines.
