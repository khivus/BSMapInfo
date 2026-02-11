import json
import os
import numpy as np
from pathlib import Path

from info_schema_version_handler import info_schema_version_handler
from level_schema_version_handler import level_schema_version_handler


VERSION = "0.0.3"
AUTHOR = "Khivus"
APP_NAME = "BSMapInfo"


# settings handled
bin_size = 3
min_idle_time = 3
stacked_counted = True
different_color_counted = True

# settings managment
app_dir = Path(os.path.expanduser("~")) / "AppData" / "Roaming" / APP_NAME
app_dir.mkdir(parents=True, exist_ok=True)
settings_file = app_dir / "settings.json"

# directory managment
target_dir = "D:\Git\BSMapInfo Test Maps"
os.chdir(target_dir)

for item in os.listdir():
    
    item_path = os.path.join(os.getcwd(), item)
    if not os.path.isdir(item_path):
        continue

    info_file_path = os.path.join(item_path, "Info.dat")
    map = info_schema_version_handler(filepath=info_file_path)

    for map_level in map.levels:

        level_file_path = os.path.join(item_path, map_level["filename"])

        level = level_schema_version_handler(characteristic=map_level["characteristic"], difficulty=map_level["difficulty"], filepath=level_file_path)

        if not level.notes_in_beats:
            print(f"\nCan't find notes in map {map.song_title} ({level.characteristic} {level.difficulty})!")
            continue
            # raise Exception(f"Notes in map {map.song_title} ({level.characteristic} {level.difficulty}) not found!")

        level.beats_to_seconds(bpm=map.bpm)
        level.count_notes_density(bin_size=bin_size, stacked_counted=stacked_counted, different_color_counted=different_color_counted)
        level.count_short_stats(bin_size=bin_size, min_idle_time=min_idle_time)

        print(f"\n{map.song_title}: {level.characteristic} {level.difficulty}")
        print(f"NPS: max = {level.max_nps:.2f}, min = {level.min_nps:.2f}, mean = {level.mean_nps:.2f}")
        print(f"Song duration: {map.song_duration if map.song_duration else level.notes_density[len(level.notes_density) - 1]['end']} sec, idle time: {level.sum_idle} sec")
        # print(f"Idle time distribution:")
        # for countdown in idle_time:
        #     print(f"{countdown['start']}-{countdown['end']}: {countdown['duration']}")
        # for countdown in level.notes_density:
        #     print(f"{countdown['start']}: {countdown['nps']:.2f}")