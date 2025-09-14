import time
import os
import RPi.GPIO as GPIO
from luma.core.interface.serial import i2c
from luma.core.render import canvas
from luma.oled.device import sh1106
from PIL import Image, ImageDraw

# --- Mode Imports ---
from modes.stats import StatsMode
from modes.music import MusicMode
from modes.game import GameMode
from modes.bluetooth import BluetoothMode
from modes.wifi import WifiMode
from modes.terminal import TerminalMode

# --- Configuration ---
ROW_PINS = [23, 24, 25, 26]
COL_PINS = [5, 6]
KEY_MAP = {
    (0, 0): "W", (0, 1): "A_RIGHT",
    (1, 0): "S", (1, 1): "B",
    (2, 0): "A_LEFT", (2, 1): "START",
    (3, 0): "D", (3, 1): "SELECT"
}

# --- File Paths ---
MUSIC_DIR = "/home/soul/piboy/Music"
ROMS_DIR = "/home/soul/piboy/piboy/roms"

# --- Device Setup ---
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
for pin in ROW_PINS:
    GPIO.setup(pin, GPIO.OUT)
for pin in COL_PINS:
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

serial = i2c(port=1, address=0x3C)
device = sh1106(serial)

# --- Global State ---
last_press_time = 0

# --- Helper Functions ---
def get_key_press():
    """Scans the button matrix and returns the pressed key or None."""
    global last_press_time
    if time.time() - last_press_time < 0.2:
        return None

    # Make sure all rows are HIGH first
    for r_pin in ROW_PINS:
        GPIO.output(r_pin, GPIO.HIGH)

    for r_idx, r_pin in enumerate(ROW_PINS):
        # Pull one row LOW
        GPIO.output(r_pin, GPIO.LOW)
        for c_idx, c_pin in enumerate(COL_PINS):
            # Check if the column is pulled LOW by the key press
            if GPIO.input(c_pin) == GPIO.LOW:
                # Key press detected, debounce and return
                last_press_time = time.time()
                # Restore the row to HIGH before returning
                GPIO.output(r_pin, GPIO.HIGH)
                return KEY_MAP.get((r_idx, c_idx), None)
        # Restore the row to HIGH before checking the next row
        GPIO.output(r_pin, GPIO.HIGH)

    return None

# --- Setup Function ---
def setup():
    """Creates directories if they don't exist."""
    print("Running initial setup...")
    for path in [MUSIC_DIR, ROMS_DIR]:
        if not os.path.exists(path):
            os.makedirs(path)
            print(f"Created directory: {path}")

# --- Main Loop ---
def main():
    setup()

    modes = [
        StatsMode(device),
        MusicMode(device, MUSIC_DIR),
        GameMode(device, ROMS_DIR),
        BluetoothMode(device),
        WifiMode(device),
        TerminalMode(device)
    ]
    current_mode_index = 0
    modes[current_mode_index].activate()

    while True:
        key = get_key_press()
        if key:
            print(f"Key: {key}")

        current_mode = modes[current_mode_index]

        # Check if a game is running in GameMode
        is_game_running = False
        if isinstance(current_mode, GameMode):
            is_game_running = current_mode.is_game_running()

        if key == "SELECT" and not is_game_running:
            current_mode.deactivate()
            current_mode_index = (current_mode_index + 1) % len(modes)
            modes[current_mode_index].activate()
            print(f"Switched to mode: {modes[current_mode_index].name}")
        else:
            current_mode.handle_input(key)

        # Specific checks for modes that need them
        if isinstance(modes[current_mode_index], MusicMode):
            modes[current_mode_index].check_music_end()

        with canvas(device) as draw:
            current_mode_name = modes[current_mode_index].name
            modes[current_mode_index].draw(draw, current_mode_name)

        time.sleep(0.05)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Exiting.")
        # Deactivate current mode to clean up resources (e.g., stop music)
        # This part needs access to modes and current_mode_index, so it's tricky
        # A simple GPIO cleanup is safe.
        GPIO.cleanup()