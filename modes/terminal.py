import os
import subprocess
import time
import select
from PIL import ImageFont

# The new terminal mode requires the 'evdev' library.
# Please install it by running: pip install evdev
try:
    from evdev import InputDevice, categorize, ecodes, util
except ImportError:
    print("ERROR: The 'evdev' library is not installed.")
    print("Please run 'pip install evdev' to use the Terminal mode.")
    # Create a dummy class to prevent crashes if evdev is not installed
    class InputDevice: pass
    class ecodes: pass


# --- CONFIGURATION ---
# This is the path to your USB keyboard. You might need to change 'event0'.
# Run 'ls /dev/input/' to see a list of available devices.
KEYBOARD_DEVICE_PATH = '/dev/input/event2' 
# --- END CONFIGURATION ---


# Scancode mapping (US keyboard layout, no shift/ctrl)
# This is a simplified map. For full shift/ctrl/alt support, this would need to be expanded.
scancodes = {
    ecodes.KEY_A: 'a', ecodes.KEY_B: 'b', ecodes.KEY_C: 'c', ecodes.KEY_D: 'd',
    ecodes.KEY_E: 'e', ecodes.KEY_F: 'f', ecodes.KEY_G: 'g', ecodes.KEY_H: 'h',
    ecodes.KEY_I: 'i', ecodes.KEY_J: 'j', ecodes.KEY_K: 'k', ecodes.KEY_L: 'l',
    ecodes.KEY_M: 'm', ecodes.KEY_N: 'n', ecodes.KEY_O: 'o', ecodes.KEY_P: 'p',
    ecodes.KEY_Q: 'q', ecodes.KEY_R: 'r', ecodes.KEY_S: 's', ecodes.KEY_T: 't',
    ecodes.KEY_U: 'u', ecodes.KEY_V: 'v', ecodes.KEY_W: 'w', ecodes.KEY_X: 'x',
    ecodes.KEY_Y: 'y', ecodes.KEY_Z: 'z',
    ecodes.KEY_1: '1', ecodes.KEY_2: '2', ecodes.KEY_3: '3', ecodes.KEY_4: '4',
    ecodes.KEY_5: '5', ecodes.KEY_6: '6', ecodes.KEY_7: '7', ecodes.KEY_8: '8',
    ecodes.KEY_9: '9', ecodes.KEY_0: '0',
    ecodes.KEY_SPACE: ' ', ecodes.KEY_MINUS: '-', ecodes.KEY_EQUAL: '=',
    ecodes.KEY_DOT: '.', ecodes.KEY_SLASH: '/', ecodes.KEY_COMMA: ",",
    ecodes.KEY_SEMICOLON: ';', ecodes.KEY_APOSTROPHE: "'", ecodes.KEY_GRAVE: '`',
    ecodes.KEY_LEFTBRACE: '[', ecodes.KEY_RIGHTBRACE: ']', ecodes.KEY_BACKSLASH: '\\',
}

class TerminalMode:
    def __init__(self, device):
        self.device = device
        self.name = "TERMINAL"
        self.font = ImageFont.load_default()
        self.keyboard = None
        self.command_buffer = ""
        self.output_lines = ["Connect a USB keyboard."]
        self.is_displaying_output = True # Start by showing the welcome/error message

    def activate(self):
        """Called when mode becomes active. Tries to connect to the keyboard."""
        self.command_buffer = ""
        try:
            # Check if evdev is installed before trying to use it
            if 'evdev' not in globals():
                raise ImportError("evdev not found")
            self.keyboard = InputDevice(KEYBOARD_DEVICE_PATH)
            self.output_lines = [f"Keyboard connected:", f"{self.keyboard.name}"]
            print(f"Terminal Mode: Listening to keyboard '{self.keyboard.name}'")
        except (ImportError, FileNotFoundError, PermissionError) as e:
            self.keyboard = None
            if isinstance(e, ImportError):
                 self.output_lines = ["Error: evdev library", "is not installed.", "Run: pip install evdev"]
            elif isinstance(e, PermissionError):
                self.output_lines = ["Error: Permission denied.", "Run script with sudo."]
            else:
                self.output_lines = [f"Keyboard not found at:", f"{KEYBOARD_DEVICE_PATH}"]
            print(f"Terminal Mode Error: {self.output_lines}")


    def deactivate(self):
        """Called when mode becomes inactive."""
        # The keyboard device is automatically released when the object is destroyed.
        self.keyboard = None
        self.is_displaying_output = False

    def run_command(self, command):
        """Executes a command and returns its output as a list of lines."""
        if not command:
            return [""]

        if command.startswith("cd "):
            try:
                path = command.split(None, 1)[1]
                os.chdir(os.path.expanduser(path))
                return [f"New Dir:", os.getcwd()]
            except Exception as e:
                return [f"Error: {str(e)}"]

        try:
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True, timeout=15
            )
            output = result.stdout + result.stderr
            # Word wrap the output to fit the screen width (approx 21 chars)
            wrapped_lines = []
            for line in output.strip().split('\n'):
                while len(line) > 21:
                    wrapped_lines.append(line[:21])
                    line = line[21:]
                wrapped_lines.append(line)
            return wrapped_lines
        except Exception as e:
            return [f"Failed:", f"{str(e)}"]

    def handle_input(self, key):
        """Handles input from both the GPIO buttons and the external keyboard."""
        # If we are showing output, any GPIO key press returns to the prompt
        if self.is_displaying_output:
            if key:
                self.is_displaying_output = False
            return

        if not self.keyboard:
            return

        # Check for external keyboard input without blocking
        r, _, _ = select.select([self.keyboard.fd], [], [], 0)
        if not r:
            return

        try:
            for event in self.keyboard.read():
                if event.type == ecodes.EV_KEY and event.value == 1: # Key press
                    key_code = event.code

                    if key_code == ecodes.KEY_ENTER:
                        self.output_lines = self.run_command(self.command_buffer)
                        self.command_buffer = ""
                        self.is_displaying_output = True
                    elif key_code == ecodes.KEY_BACKSPACE:
                        self.command_buffer = self.command_buffer[:-1]
                    else:
                        # This part handles shift keys for capitalization
                        caps = util.is_caps_lock_on(self.keyboard)
                        shift = self.keyboard.leds()[ecodes.LED_SHIFT]

                        char = scancodes.get(key_code)
                        if char:
                            if (shift or caps):
                                self.command_buffer += char.upper()
                            else:
                                self.command_buffer += char

        except (IOError, OSError):
            # This can happen if the keyboard is disconnected
            self.keyboard = None
            self.output_lines = ["Keyboard disconnected."]
            self.is_displaying_output = True


    def draw(self, draw, current_mode_name):
        """Draws the terminal UI."""
        if self.is_displaying_output:
            draw.text((0, 0), "--- Output ---", font=self.font, fill="white")
            for i, line in enumerate(self.output_lines):
                if i < 7: # Leave one line for the prompt to return
                    draw.text((0, (i + 1) * 8), line, font=self.font, fill="white")
            draw.text((0, 56), "Press any key to close", font=self.font, fill="white")
        else:
            # Add a blinking cursor effect
            cursor = "_" if int(time.time() * 2) % 2 == 0 else " "
            prompt = f"> {self.command_buffer}"
            draw.text((0, 0), prompt + cursor, font=self.font, fill="white")
            # Display current directory
            pwd = os.getcwd()
            # Truncate PWD if too long
            if len(pwd) > 21:
                pwd = "..." + pwd[-18:]
            draw.text((0, 56), pwd, font=self.font, fill="white")