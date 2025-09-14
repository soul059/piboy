import time
import subprocess
import threading
from PIL import ImageFont
from .ui import draw_menu, MAX_MENU_ITEMS

class WifiMode:
    def __init__(self, device):
        self.device = device
        self.name = "WIFI"
        self.wifi_networks = []
        self.selected_wifi_index = 0
        self.is_entering_password = False
        self.current_password = ""
        self.password_entry_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-="
        self.char_cursor_pos = 0
        self.menu_scroll_offset = 0
        self.is_scanning = False

    def get_wifi_status(self):
        try:
            cmd = "nmcli -t -f ACTIVE,SSID dev wifi | egrep '^yes' | cut -d':' -f2"
            ssid = subprocess.check_output(cmd, shell=True, text=True).strip()
            return f"Connected: {ssid}" if ssid else "Disconnected"
        except subprocess.CalledProcessError:
            return "Disconnected"

    def _scan_worker(self):
        """Worker thread for scanning networks."""
        print("Scanning for WiFi networks...")
        try:
            cmd = "nmcli --terse --fields SSID dev wifi list | awk '!seen[$0]++'"
            result = subprocess.check_output(cmd, shell=True, text=True)
            ssids = [line.strip() for line in result.splitlines() if line.strip()]
            self.wifi_networks = ssids
        except subprocess.CalledProcessError:
            self.wifi_networks = []
        finally:
            self.is_scanning = False
            print("Scan finished.")

    def scan_wifi_networks(self):
        """Starts a non-blocking WiFi scan."""
        if not self.is_scanning:
            self.is_scanning = True
            self.wifi_networks = [] # Clear old results
            scan_thread = threading.Thread(target=self._scan_worker)
            scan_thread.start()

    def connect_to_wifi(self, ssid, password):
        print(f"Attempting to connect to {ssid}...")
        try:
            cmd = f"nmcli dev wifi connect '{ssid}' password '{password}'"
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            print("Connection command sent.")
            time.sleep(8)
        except subprocess.CalledProcessError as e:
            print(f"Failed to connect: {e.stderr.decode()}")

    def handle_input(self, key):
        if self.is_entering_password:
            if key == "D": self.char_cursor_pos = (self.char_cursor_pos + 1) % len(self.password_entry_chars)
            elif key == "A_LEFT": self.char_cursor_pos = (self.char_cursor_pos - 1 + len(self.password_entry_chars)) % len(self.password_entry_chars)
            elif key == "B": self.current_password += self.password_entry_chars[self.char_cursor_pos]
            elif key == "A_RIGHT": self.current_password = self.current_password[:-1]
            elif key == "START":
                if self.wifi_networks:
                    ssid = self.wifi_networks[self.selected_wifi_index]
                    self.connect_to_wifi(ssid, self.current_password)
                self.is_entering_password = False
                self.current_password = ""
        else: # In network list
            if key == "S": self.selected_wifi_index = (self.selected_wifi_index + 1) % len(self.wifi_networks) if self.wifi_networks else 0
            elif key == "W": self.selected_wifi_index = (self.selected_wifi_index - 1 + len(self.wifi_networks)) % len(self.wifi_networks) if self.wifi_networks else 0
            elif key == "D": self.scan_wifi_networks()
            elif key == "B" or key == "START":
                if self.wifi_networks:
                    self.is_entering_password = True
                    self.current_password = ""
                    self.char_cursor_pos = 0
            
            if self.selected_wifi_index < self.menu_scroll_offset:
                self.menu_scroll_offset = self.selected_wifi_index
            elif self.selected_wifi_index >= self.menu_scroll_offset + MAX_MENU_ITEMS:
                self.menu_scroll_offset = self.selected_wifi_index - MAX_MENU_ITEMS + 1

    def draw(self, draw, current_mode_name):
        if self.is_entering_password:
            self.draw_password_entry(draw)
        else:
            font = ImageFont.load_default()
            status = self.get_wifi_status()
            title = "Scanning..." if self.is_scanning else status
            draw_menu(draw, title, self.wifi_networks, self.selected_wifi_index, self.menu_scroll_offset)
            controls = "W/S:Scroll B:Select D:Scan"
            draw.text((0, 54), controls, fill="white", font=font)

    def draw_password_entry(self, draw):
        font = ImageFont.load_default()
        ssid = self.wifi_networks[self.selected_wifi_index]
        draw.text((0, 0), f"Pass for {ssid[:15]}:", fill="white", font=font)
        
        draw.rectangle((0, 12, self.device.width, 24), outline="white", fill="black")
        draw.text((2, 14), "*" * len(self.current_password), fill="white", font=font)

        display_chars_width = 16
        start_index = max(0, self.char_cursor_pos - (display_chars_width // 2))
        display_string = self.password_entry_chars[start_index : start_index + display_chars_width]

        for i, char in enumerate(display_string):
            x = i * 8
            if (start_index + i) == self.char_cursor_pos:
                 draw.rectangle((x, 28, x + 7, 38), fill="white")
                 draw.text((x + 1, 28), char, fill="black", font=font)
            else:
                 draw.text((x + 1, 28), char, fill="white", font=font)

        draw.text((0, 42), "A_L/D:Select B:Add", fill="white", font=font)
        draw.text((0, 52), "START:Go A_R:Back", fill="white", font=font)

    def activate(self):
        self.menu_scroll_offset = 0
        self.is_entering_password = False
        self.scan_wifi_networks()

    def deactivate(self):
        self.is_entering_password = False