import os
import json
import numpy as np

from scipy.stats import kurtosis

from map_handler import MapHandler
from settings_handler import SettingsHandler


class LevelHandler:
    
    level_major_version: int
    characteristic: str
    difficulty: str
    njs: float
    filename: str
    notes_in_beats: list
    notes_in_seconds: list
    notes_density: list
    max_nps: float
    min_nps: float
    mean_nps: float
    sum_idle: float
    idle_time: list
    bad_mapper: bool = False


    def __init__(self, map: MapHandler, settings: SettingsHandler, level_index: int):

        self.characteristic = map.levels[level_index]["characteristic"]
        self.difficulty = map.levels[level_index]["difficulty"]
        self.njs = map.levels[level_index]["njs"]

        filepath = os.path.join(map.map_path, map.levels[level_index]["filename"])

        with open(filepath, 'r', encoding="utf-8") as file:
            self.level_json = json.load(file)

        try:
            self.level_major_version = int(self.level_json["version"].split('.')[0])
        except:
            self.level_major_version = int(self.level_json["_version"].split('.')[0])

        if self.level_major_version == 2:
            self.v2_handler()
        elif self.level_major_version == 3:
            self.v3_handler()
        else:
            self.v4_handler()

        if not self.notes_in_beats:
            return

        self.beats_to_seconds(map.bpm, map.bpm_regions, map.sample_count, map.song_duration)
        self.count_notes_density(bin_size=settings.bin_size, merge_same_color_stacks=settings.merge_same_color_stacks.get(), merge_mixed_color_stacks=settings.merge_mixed_color_stacks.get())
        self.count_short_stats(bin_size=settings.bin_size, min_idle_time=settings.min_idle_time)


    def v2_handler(self):
        notes = []
        for note in self.level_json["_notes"]:
            try:
                if note["_type"] == 3: # bomb
                    continue
                notes.append({"beat" : note["_time"], "color" : note["_type"]})
            except:
                self.bad_mapper = True

        self.notes_in_beats = notes


    def v3_handler(self):
        notes = []
        for note in self.level_json["colorNotes"]:
            try:
                notes.append({"beat" : note["b"], "color" : note["c"]})
            except:
                self.bad_mapper = True
        
        self.notes_in_beats = notes


    def v4_handler(self):
        notes = []
        for note in self.level_json["colorNotes"]:
            try:
                notes.append({"beat" : note["b"], "color" : self.level_json["colorNotesData"][note["i"]]["c"]})
            except:
                self.bad_mapper = True

        self.notes_in_beats = notes


    # def beats_to_seconds(self, bpm: float):
    #     notes = []
    #     for note in self.notes_in_beats:
    #         note_sec = (note["beat"] * 60) / bpm
    #         notes.append({"beat" : note_sec, "color" : note["color"]})
        
    #     self.notes_in_seconds = notes


    def beats_to_seconds(self, global_bpm: float, regions: list, sample_count: int, song_length: float):

        if not regions or not sample_count:
            self.notes_in_seconds = [
                {
                    "beat": note["beat"] * 60.0 / global_bpm,
                    "color": note["color"]
                }
                for note in self.notes_in_beats
            ]
            return
        
        sample_rate = sample_count / song_length
        prepared_regions = []
        for r in regions:
            samples = r["end_sample_index"] - r["start_sample_index"]
            seconds = samples / sample_rate
            beats = r["end_beat"] - r["start_beat"]

            region_bpm = beats / seconds * 60.0

            prepared_regions.append({
                "startBeat": r["start_beat"],
                "endBeat": r["end_beat"],
                "bpm": region_bpm
            })

        prepared_regions.sort(key=lambda x: x["startBeat"])

        def beat_to_sec(target_beat: float) -> float:
            time_sec = 0.0
            current_beat = 0.0

            for reg in prepared_regions:

                if target_beat <= reg["startBeat"]:
                    time_sec += (target_beat - current_beat) * 60.0 / global_bpm
                    return time_sec

                time_sec += (reg["startBeat"] - current_beat) * 60.0 / global_bpm
                current_beat = reg["startBeat"]

                if target_beat <= reg["endBeat"]:
                    time_sec += (target_beat - current_beat) * 60.0 / reg["bpm"]
                    return time_sec

                time_sec += (reg["endBeat"] - current_beat) * 60.0 / reg["bpm"]
                current_beat = reg["endBeat"]

            time_sec += (target_beat - current_beat) * 60.0 / global_bpm
            return time_sec

        result = []
        for note in self.notes_in_beats:
            sec = beat_to_sec(note["beat"])
            result.append({
                "beat": sec,
                "color": note["color"]
            })

        self.notes_in_seconds = result

    
    def count_notes_density(self, bin_size : int, merge_same_color_stacks: bool, merge_mixed_color_stacks: bool): # Returns list of counted notes in list
        stop = self.notes_in_seconds[len(self.notes_in_seconds) - 1]["beat"] + bin_size

        raw_notes = []
        seen_stacked = {}
        seen_different = {}

        for index, note in enumerate(self.notes_in_seconds):
            beat = note["beat"]
            color = note["color"]
            
            stacked_exists = (beat, color) in seen_stacked
            different_color_exists = (beat, not color) in seen_different

            if stacked_exists and merge_same_color_stacks:
                continue
            if different_color_exists and merge_mixed_color_stacks:
                continue

            raw_notes.append(beat)

            seen_stacked[(beat, color)] = index
            seen_different[(beat, color)] = index

        bins = np.arange(0, stop, bin_size)
        counts, edges = np.histogram(raw_notes, bins=bins)
        
        self.counts = counts
        self.edges = edges
        
        density = []
        for i in range(len(edges) - 1):
            density.append({"start" : int(edges[i]), "end" : int(edges[i+1]), "nps" : counts[i] / bin_size})

        self.notes_density = density


    def count_short_stats(self, bin_size: int, min_idle_time: int):
        raw_vals = []

        for note in self.notes_density:
            raw_vals.append(note["nps"])

        values = np.array(raw_vals)
        non_zero = values[values != 0]

        idle_time = []
        index = 0
        last_note = {"nps" : 1337}

        for note in self.notes_density:
            if note["nps"] == 0 and last_note["nps"] != 0:
                idle_time.append({
                    "start" : note["start"],
                    "end" : note["end"],
                    "duration" : bin_size
                })
            elif note["nps"] == 0 and last_note["nps"] == 0:
                idle_time[index]["end"] = note["end"]
                idle_time[index]["duration"] += bin_size
            elif note["nps"] != 0 and last_note["nps"] == 0:
                index += 1
            last_note = note

        if min_idle_time <= bin_size:
            self.sum_idle = sum(x["duration"] for x in idle_time)
        else:
            self.sum_idle = sum(x["duration"] for x in idle_time if x["duration"] > min_idle_time)

        sorted = non_zero
        sorted.sort()
        sorted_len = len(sorted)
        self.median = sorted[sorted_len // 2] if  not sorted_len % 2 else (sorted[sorted_len // 2] + sorted[(sorted_len // 2) + 1]) / 2

        self.max_nps = np.max(non_zero)
        self.min_nps = np.min(non_zero)
        self.mean_nps = float(np.mean(non_zero))
        self.standard_deviation = np.std(non_zero, ddof=1)
        self.kurtosis = kurtosis(non_zero)
        self.idle_time = self.time_adjust(self.sum_idle)

    
    def time_adjust(self, time) -> list:
        if time >= 60:
            return [round(time // 60), round(time % 60)]
        else:
            return [0, round(time)]