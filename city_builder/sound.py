# Elite 1984 City Builder - Sound Management

import pygame as pg

class SoundManager:
    def __init__(self):
        self.sounds = {}
        self.is_muted = False
        # It's good practice to initialize mixer with preferred settings
        # pg.mixer.init(frequency=44100, size=-16, channels=2, buffer=512) # Example settings

    def load_sound(self, name: str, filepath: str):
        """Loads a sound effect and stores it."""
        if not pg.mixer.get_init(): # Initialize mixer if not already done
            pg.mixer.init()
            print("Pygame mixer initialized by SoundManager.")

        try:
            sound = pg.mixer.Sound(filepath)
            self.sounds[name] = sound
        except pg.error as e:
            print(f"Warning: Could not load sound '{name}' from '{filepath}': {e}")
            self.sounds[name] = None # Store None so we don't try to load it again

    def play(self, name: str, loops: int = 0, volume: float = 1.0):
        """Plays a loaded sound effect."""
        if self.is_muted:
            return

        if name in self.sounds and self.sounds[name] is not None:
            sound_to_play = self.sounds[name]
            sound_to_play.set_volume(volume)
            sound_to_play.play(loops=loops)
        elif name not in self.sounds:
            print(f"Warning: Sound '{name}' not loaded. Call load_sound first.")
        # If self.sounds[name] is None, it means loading failed, warning already printed.

    def toggle_mute(self):
        """Toggles sound playback on/off."""
        self.is_muted = not self.is_muted
        if self.is_muted:
            pg.mixer.stop() # Stop all currently playing sounds
            print("Sound muted.")
        else:
            print("Sound unmuted.")

    def set_master_volume(self, master_volume: float):
        """
        Sets a master volume for all sounds.
        Note: Pygame's mixer doesn't have a direct master volume for Sound objects after they are played.
        This method is a placeholder or would require adjusting individual sound plays.
        A common approach is to store the master volume and apply it when self.play() is called.
        For now, this is a conceptual placeholder.
        """
        print(f"Master volume conceptually set to {master_volume}. Individual sound volumes are set at play time.")


# Example usage (requires actual sound files in an 'assets/sounds' directory for testing)
if __name__ == "__main__":
    pg.init() # Pygame needs to be initialized for sound
    # screen = pg.display.set_mode((100,100)) # Mixer might need a display in some pg versions/OS

    sound_manager = SoundManager()

    # Create dummy sound files for testing if they don't exist
    # This part is just for local testing of this script
    import os
    assets_sounds_dir = "assets/sounds"
    if not os.path.exists(assets_sounds_dir):
        os.makedirs(assets_sounds_dir)

    dummy_click_path = os.path.join(assets_sounds_dir, "ui_click.wav")
    dummy_place_path = os.path.join(assets_sounds_dir, "build_place.wav")

    # Create very simple WAV files if they don't exist (requires scipy for this example)
    try:
        from scipy.io.wavfile import write as write_wav
        import numpy as np

        if not os.path.exists(dummy_click_path):
            samplerate = 44100; fs = 100
            t = np.linspace(0., 0.1, int(samplerate * 0.1)) # 0.1 seconds
            data = np.sin(2. * np.pi * 220. * t) * 0.5 # A4 note
            write_wav(dummy_click_path, samplerate, data.astype(np.float32))
            print(f"Created dummy sound: {dummy_click_path}")

        if not os.path.exists(dummy_place_path):
            samplerate = 44100; fs = 100
            t = np.linspace(0., 0.2, int(samplerate * 0.2)) # 0.2 seconds
            data = np.sin(2. * np.pi * 440. * t) * 0.5 # A5 note
            write_wav(dummy_place_path, samplerate, data.astype(np.float32))
            print(f"Created dummy sound: {dummy_place_path}")

    except ImportError:
        print("SciPy not installed. Cannot create dummy WAV files for testing sound.py.")
        print(f"Please create '{dummy_click_path}' and '{dummy_place_path}' manually if you want to test sounds.")


    sound_manager.load_sound("ui_click", dummy_click_path)
    sound_manager.load_sound("build_place", dummy_place_path)
    sound_manager.load_sound("non_existent", "assets/sounds/no.wav") # Test failed load

    print("Playing click sound...")
    sound_manager.play("ui_click")
    pg.time.wait(200) # Wait for sound to play a bit

    print("Playing build place sound with lower volume...")
    sound_manager.play("build_place", volume=0.5)
    pg.time.wait(300)

    print("Toggling mute...")
    sound_manager.toggle_mute()
    sound_manager.play("ui_click") # Should not play
    pg.time.wait(200)
    print("Toggling mute again...")
    sound_manager.toggle_mute()
    sound_manager.play("ui_click") # Should play
    pg.time.wait(200)

    pg.quit()
