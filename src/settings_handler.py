import os
import json
import customtkinter as ctk

from pathlib import Path


class SettingsHandler:

    default_settings = {
        "target_dir" : "",
        "geometry" : "870x500+D+D",
        "bin_size" : 3,
        "min_idle_time" : 3,
        "merge_same_color_stacks" : False,
        "merge_mixed_color_stacks" : False,
        "sort_order" : "song_title",
        "sort_direction" : 0
    }

    def __init__(self, app_instance, app_name) -> None:
        local_appdata = os.getenv('LOCALAPPDATA')
        if not local_appdata:
            raise RuntimeError("LOCALAPPDATA not found!")

        app_dir = Path(local_appdata) / app_name
        app_dir.mkdir(parents=True, exist_ok=True)
        self.settings_file = app_dir / "settings.json"

        # self.settings_file.unlink()
        
        self.__app__ = app_instance
        self._load_settings()
        self._calculate_geometry()


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
        self.merge_same_color_stacks = ctk.BooleanVar(value=self._settings["merge_same_color_stacks"])
        self.merge_mixed_color_stacks = ctk.BooleanVar(value=self._settings["merge_mixed_color_stacks"])
        self.sort_order = self._settings["sort_order"]
        self.sort_direction = self._settings["sort_direction"]


    def _calculate_geometry(self):
        size, x, y = self.geometry.split('+')
        width, height = size.split('x')

        if x == "D":
            x = (self.__app__.winfo_screenwidth() - int(width)) // 2

        if y == "D":
            y = (self.__app__.winfo_screenheight() - int(height)) // 2

        self.geometry = f"{width}x{height}+{x}+{y}"


    def save_settings(self):
        settings = {}
        settings["target_dir"] = self.target_dir
        settings["geometry"] = self.geometry
        settings["bin_size"] = self.bin_size
        settings["min_idle_time"] = self.min_idle_time
        settings["merge_same_color_stacks"] = self.merge_same_color_stacks.get()
        settings["merge_mixed_color_stacks"] = self.merge_mixed_color_stacks.get()
        settings["sort_order"] = self.sort_order
        settings["sort_direction"] = self.sort_direction

        with open(self.settings_file, 'w', encoding='utf-8') as file:
            json.dump(settings, file, indent=4, ensure_ascii=False)