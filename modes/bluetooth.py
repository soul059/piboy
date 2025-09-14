import subprocess
from PIL import ImageFont

class BluetoothMode:
    def __init__(self, device):
        self.device = device
        self.name = "BLUETOOTH"

    def get_bt_status(self):
        """Checks bluetooth connection status."""
        try:
            info = subprocess.check_output("bluetoothctl info", shell=True, text=True, stderr=subprocess.DEVNULL)
            for line in info.splitlines():
                if "Name:" in line:
                    device_name = line.split("Name: ")[1]
                    return f"Connected to:\n {device_name}"
        except subprocess.CalledProcessError:
            return "Waiting for a\n connection..."
        return "Status Unknown"

    def handle_input(self, key):
        pass

    def draw(self, draw, current_mode_name):
        """UI for Bluetooth status."""
        font = ImageFont.load_default()
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        hostname = subprocess.check_output("hostname", shell=True).decode('utf-8').strip()
        status = self.get_bt_status()
        draw.text((0, 0), "--- BLUETOOTH AUDIO ---", fill="white", font=font)
        draw.text((5, 15), f"Name: {hostname}", fill="white", font=font)
        draw.text((5, 35), status, fill="white", font=font_large)

    def activate(self):
        pass

    def deactivate(self):
        pass
