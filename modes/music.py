import os
import subprocess
import signal
from PIL import ImageFont
from .ui import draw_menu, MAX_MENU_ITEMS

class MusicMode:
    def __init__(self, device, music_dir):
        self.device = device
        self.name = "MUSIC"
        self.music_dir = music_dir
        self.music_files = []
        self.current_song_index = 0
        self.is_playing = False
        self.is_paused = False
        self.music_process = None
        self.menu_scroll_offset = 0
        self.show_menu = True

    def stop_music(self):
        """Stops the currently playing music."""
        if self.music_process:
            # Use SIGTERM to allow clean exit if possible, then kill
            self.music_process.terminate()
            try:
                self.music_process.wait(timeout=0.5)
            except subprocess.TimeoutExpired:
                self.music_process.kill()
            self.music_process = None
        self.is_playing = False
        self.is_paused = False

    def play_music(self, index):
        """Plays the selected song."""
        self.stop_music()
        if self.music_files:
            self.current_song_index = index
            song_path = self.music_files[self.current_song_index]
            # Using -C flag allows for some terminal-based control, though we use signals
            self.music_process = subprocess.Popen(["mpg123", "-q", "-o", "alsa", song_path])
            self.is_playing = True
            self.is_paused = False

    def handle_input(self, key):
        """Handles all user input for music mode."""
        if key == 'A_RIGHT':
            self.show_menu = not self.show_menu
            return

        if self.show_menu:
            # Menu navigation
            if not self.music_files:
                return

            if key == 'W':  # Up
                self.current_song_index = (self.current_song_index - 1 + len(self.music_files)) % len(self.music_files)
            elif key == 'S':  # Down
                self.current_song_index = (self.current_song_index + 1) % len(self.music_files)
            elif key == 'B' or key == 'START':  # Play selected song
                self.play_music(self.current_song_index)
                self.show_menu = False  # Switch to player view

            # Adjust menu scroll offset
            if self.current_song_index < self.menu_scroll_offset:
                self.menu_scroll_offset = self.current_song_index
            elif self.current_song_index >= self.menu_scroll_offset + MAX_MENU_ITEMS:
                self.menu_scroll_offset = self.current_song_index - MAX_MENU_ITEMS + 1
        
        elif self.is_playing:  # In player view and a song is playing
            if key == 'W':  # Pause/Resume
                if self.is_paused:
                    self.music_process.send_signal(signal.SIGCONT)
                    self.is_paused = False
                else:
                    self.music_process.send_signal(signal.SIGSTOP)
                    self.is_paused = True
            elif key == 'A_LEFT':  # Previous Track
                prev_index = (self.current_song_index - 1 + len(self.music_files)) % len(self.music_files)
                self.play_music(prev_index)
            elif key == 'D':  # Next Track
                next_index = (self.current_song_index + 1) % len(self.music_files)
                self.play_music(next_index)
            elif key == 'S' or key == 'B':  # Stop
                self.stop_music()
                self.show_menu = True


    def draw(self, draw, current_mode_name):
        """UI for the music player."""
        font = ImageFont.load_default()
        
        if self.show_menu:
            draw_menu(draw, "MUSIC", self.music_files, self.current_song_index, self.menu_scroll_offset)
        elif self.is_playing:
            draw.text((0, 0), "--- NOW PLAYING ---", fill="white", font=font)
            song_name = os.path.basename(self.music_files[self.current_song_index])
            if len(song_name) > 20:
                song_name = song_name[:17] + "..."
            
            play_status = " (Paused)" if self.is_paused else ""
            draw.text((5, 20), song_name + play_status, fill="white", font=font)

            controls = "W:Resume, A/D:Track, S:Stop" if self.is_paused else "W:Pause, A/D:Track, S:Stop"
            draw.text((5, 35), controls, fill="white", font=font)
        else:
            draw.text((0, 0), "--- MUSIC ---", fill="white", font=font)
            draw.text((5, 20), "Nothing is playing", fill="white", font=font)

    def check_music_end(self):
        """Checks if the song has ended and plays the next one."""
        if self.is_playing and not self.is_paused and self.music_process and self.music_process.poll() is not None:
             next_index = (self.current_song_index + 1) % len(self.music_files)
             self.play_music(next_index)

    def activate(self):
        """Scans for music files when mode is activated."""
        self.music_files = sorted([os.path.join(self.music_dir, f) for f in os.listdir(self.music_dir) if f.endswith('.mp3')])
        self.menu_scroll_offset = 0
        print(f"Found {len(self.music_files)} music files.")

    def deactivate(self):
        """Stops music when switching away from this mode."""
        self.stop_music()