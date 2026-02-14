import os
import json
import customtkinter as ctk

from pathlib import Path


class SettingsHandler:

    default_settings = {
        "target_dir" : "",
        "geometry" : "850x500+-1+-1",
        "bin_size" : 3,
        "min_idle_time" : 3,
        "stacked_counted" : True,
        "different_color_counted" : True
    }

    def __init__(self, app_name) -> None:
        local_appdata = os.getenv('LOCALAPPDATA')
        if not local_appdata:
            raise RuntimeError("LOCALAPPDATA not found!")

        app_dir = Path(local_appdata) / app_name
        app_dir.mkdir(parents=True, exist_ok=True)
        self.settings_file = app_dir / "settings.json"

        # self.settings_file.unlink()
        
        self.load_settings()


    def load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r', encoding='utf-8') as file:
                settings_json = json.load(file)

            self._settings = {**self.default_settings, **settings_json}

        else:
            self._settings = self.default_settings.copy()
            
        self._apply_settings()


    def _apply_settings(self):
        self.target_dir = self._settings["target_dir"]
        self.geometry = self._settings["geometry"]
        self.bin_size = self._settings["bin_size"]
        self.min_idle_time = self._settings["min_idle_time"]
        self.stacked_counted = ctk.BooleanVar(value=self._settings["stacked_counted"])
        self.different_color_counted = ctk.BooleanVar(value=self._settings["different_color_counted"])


    def save_settings(self):
        settings = {}
        settings["target_dir"] = self.target_dir
        settings["geometry"] = self.geometry
        settings["bin_size"] = self.bin_size
        settings["min_idle_time"] = self.min_idle_time
        settings["stacked_counted"] = self.stacked_counted.get()
        settings["different_color_counted"] = self.different_color_counted.get()

        with open(self.settings_file, 'w', encoding='utf-8') as file:
            json.dump(settings, file, indent=4, ensure_ascii=False)