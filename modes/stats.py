import subprocess
import time
from datetime import datetime
from PIL import ImageFont

class StatsMode:
    def __init__(self, device):
        self.device = device
        self.name = "STATS"
        self.page_index = 0
        self.pages = ["CLOCK", "SYSTEM"]

    def get_clock_page_stats(self):
        """Gets CPU usage (from top), temp, and current time."""
        try:
            cpu_usage = subprocess.check_output("top -bn1 | grep 'Cpu(s)' | awk '{print $2 + $4}'", shell=True).decode('utf-8').strip()
        except subprocess.CalledProcessError:
            cpu_usage = "N/A"
        try:
            temp_raw = subprocess.check_output("cat /sys/class/thermal/thermal_zone0/temp", shell=True).decode('utf-8')
            temp = float(temp_raw) / 1000.0
            temp_str = f"T:{temp:.1f}C"
        except (subprocess.CalledProcessError, FileNotFoundError):
            temp_str = "T: N/A"
        
        now = datetime.now().strftime("%H:%M:%S")
        return f"CPU:{cpu_usage}% {temp_str}", now

    def get_system_page_stats(self):
        """Gets IP, CPU Load, Memory, and Disk stats."""
        stats = {}
        try:
            stats['IP'] = "IP: " + subprocess.check_output("hostname -I | cut -d' ' -f1", shell=True).decode("utf-8").strip()
        except subprocess.CalledProcessError:
            stats['IP'] = "IP: Not found"
        try:
            stats['CPU'] = subprocess.check_output("top -bn1 | grep load | awk '{printf \"CPU: %.2f%%\", $(NF-2)}'", shell=True).decode("utf-8")
        except subprocess.CalledProcessError:
            stats['CPU'] = "CPU: N/A"
        try:
            stats['Mem'] = subprocess.check_output("free -m | awk 'NR==2{printf \"Mem: %s/%sMB %.2f%%\", $3,$2,$3*100/$2 }'", shell=True).decode("utf-8")
        except subprocess.CalledProcessError:
            stats['Mem'] = "Mem: N/A"
        try:
            stats['Disk'] = subprocess.check_output("df -h | awk '$NF==\"/\"{printf \"Disk: %d/%dGB %s\", $3,$2,$5}'", shell=True).decode("utf-8")
        except subprocess.CalledProcessError:
            stats['Disk'] = "Disk: N/A"
        return stats

    def handle_input(self, key):
        """Switches pages on 'W' key press."""
        if key == 'W':
            self.page_index = (self.page_index + 1) % len(self.pages)

    def draw_clock_page(self, draw, current_mode_name):
        stats, current_time = self.get_clock_page_stats()
        font_small = ImageFont.load_default()
        font_large = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        draw.text((0, 0), "--- STATS & CLOCK ---", fill="white", font=font_small)
        draw.text((0, 15), current_time, fill="white", font=font_large)
        draw.text((0, 45), stats, fill="white", font=font_small)
        draw.text((0, 55), f"Mode: {current_mode_name} (W=next)", fill="white", font=font_small)

    def draw_system_page(self, draw):
        stats = self.get_system_page_stats()
        font = ImageFont.load_default()
        draw.text((0, 0), "--- SYSTEM INFO ---", font=font, fill="white")
        draw.text((0, 12), stats['IP'], font=font, fill="white")
        draw.text((0, 24), stats['CPU'], font=font, fill="white")
        draw.text((0, 36), stats['Mem'], font=font, fill="white")
        draw.text((0, 48), stats['Disk'], font=font, fill="white")

    def draw(self, draw, current_mode_name):
        """Draws the current page."""
        page_name = self.pages[self.page_index]
        if page_name == "CLOCK":
            self.draw_clock_page(draw, current_mode_name)
        elif page_name == "SYSTEM":
            self.draw_system_page(draw)

    def activate(self):
        self.page_index = 0

    def deactivate(self):
        pass