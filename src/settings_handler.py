import os
import json
import customtkinter as ctk

from pathlib import Path


class SettingsHandler:

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

            self.target_dir = settings_json["target_dir"]
            self.bin_size = settings_json["bin_size"]
            self.min_idle_time = settings_json["min_idle_time"]
            self.stacked_counted = ctk.BooleanVar(value=settings_json["stacked_counted"])
            self.different_color_counted = ctk.BooleanVar(value=settings_json["different_color_counted"])

        else:
            self.target_dir = ""
            self.bin_size = 3
            self.min_idle_time = 3
            self.stacked_counted = ctk.BooleanVar(value=True)
            self.different_color_counted = ctk.BooleanVar(value=True)


    def save_settings(self):
        settings = {}
        settings["target_dir"] = self.target_dir
        settings["bin_size"] = self.bin_size
        settings["min_idle_time"] = self.min_idle_time
        settings["stacked_counted"] = self.stacked_counted.get()
        settings["different_color_counted"] = self.different_color_counted.get()

        with open(self.settings_file, 'w', encoding='utf-8') as file:
            json.dump(settings, file, indent=4, ensure_ascii=False)