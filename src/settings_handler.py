import os
import json
import customtkinter as ctk

from pathlib import Path


class SettingsHandler:

    default_settings = {
        "target_dir" : "",
        "geometry" : "850x500+D+D",
        "bin_size" : 3,
        "min_idle_time" : 3,
        "stacked_counted" : True,
        "different_color_counted" : True,
        "sort_order" : "song_title",
        "sort_direction" : 0
    }

    def __init__(self, app_name) -> None:
        local_appdata = os.getenv('LOCALAPPDATA')
        if not local_appdata:
            raise RuntimeError("LOCALAPPDATA not found!")

        app_dir = Path(local_appdata) / app_name
        app_dir.mkdir(parents=True, exist_ok=True)
        self.settings_file = app_dir / "settings.json"

        # self.settings_file.unlink()
        
        self._load_settings()


    def _load_settings(self):
        if os.path.exists(self.settings_file):
            with open(self.settings_file, 'r', encoding='utf-8') as file:
                settings_json = json.load(file)

            self._migration(settings_json)
            self._settings = {**self.default_settings, **settings_json}

        else:
            self._settings = self.default_settings.copy()
            
        self._apply_settings()


    def _migration(self, settings_json):
        missing_keys = set(self.default_settings.keys()) - set(settings_json.keys())

        if not missing_keys:
            return

        for key in missing_keys:
            settings_json[key] = self.default_settings[key]
        
        with open(self.settings_file, 'w', encoding='utf-8') as file:
            json.dump(settings_json, file, indent=4, ensure_ascii=False)

        self._load_settings()


    def _apply_settings(self):
        self.target_dir = self._settings["target_dir"]
        self.geometry = self._settings["geometry"]
        self.bin_size = self._settings["bin_size"]
        self.min_idle_time = self._settings["min_idle_time"]
        self.stacked_counted = ctk.BooleanVar(value=self._settings["stacked_counted"])
        self.different_color_counted = ctk.BooleanVar(value=self._settings["different_color_counted"])
        self.sort_order = self._settings["sort_order"]
        self.sort_direction = self._settings["sort_direction"]


    def save_settings(self):
        settings = {}
        settings["target_dir"] = self.target_dir
        settings["geometry"] = self.geometry
        settings["bin_size"] = self.bin_size
        settings["min_idle_time"] = self.min_idle_time
        settings["stacked_counted"] = self.stacked_counted.get()
        settings["different_color_counted"] = self.different_color_counted.get()
        settings["sort_order"] = self.sort_order
        settings["sort_direction"] = self.sort_direction

        with open(self.settings_file, 'w', encoding='utf-8') as file:
            json.dump(settings, file, indent=4, ensure_ascii=False)