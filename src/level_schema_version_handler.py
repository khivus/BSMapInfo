import json
import numpy as np

class LevelSchemaVersionHandler():
    
    level_major_version: int
    characteristic: str
    difficulty: str
    filename: str
    notes_in_beats: list
    notes_in_seconds: list
    notes_density: list
    max_nps: float
    min_nps: float
    mean_nps: float
    sum_idle: float
    idle_time: list


    def __init__(self, characteristic: str, difficulty: str, filepath: str):
        self.characteristic = characteristic
        self.difficulty = difficulty

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


    def v2_handler(self):
        notes = []
        for note in self.level_json["_notes"]:
            if note["_type"] == 3: # bomb
                continue
            notes.append({"beat" : note["_time"], "color" : note["_type"]})

        self.notes_in_beats = notes


    def v3_handler(self):
        notes = []
        for note in self.level_json["colorNotes"]:
            notes.append({"beat" : note["b"], "color" : note["c"]})
        
        self.notes_in_beats = notes


    def v4_handler(self):
        notes = []
        for note in self.level_json["colorNotes"]:
            notes.append({"beat" : note["b"], "color" : self.level_json["colorNotesData"][note["i"]]["c"]})

        self.notes_in_beats = notes


    def beats_to_seconds(self, bpm: float):
        notes = []
        for note in self.notes_in_beats:
            note_sec = (note["beat"] * 60) / bpm
            notes.append({"beat" : note_sec, "color" : note["color"]})
        
        self.notes_in_seconds = notes

    
    def count_notes_density(self, bin_size : int, stacked_counted: bool, different_color_counted: bool): # Returns list of counted notes in list
        stop = self.notes_in_seconds[len(self.notes_in_seconds) - 1]["beat"] + bin_size

        raw_notes = []
        seen_stacked = {}
        seen_different = {}

        for index, note in enumerate(self.notes_in_seconds):
            beat = note["beat"]
            color = note["color"]
            
            stacked_exists = (beat, color) in seen_stacked
            different_color_exists = (beat, not color) in seen_different

            if stacked_exists and not stacked_counted:
                continue
            if different_color_exists and not different_color_counted:
                continue

            raw_notes.append(beat)

            seen_stacked[(beat, color)] = index
            seen_different[(beat, color)] = index

        bins = np.arange(0, stop, bin_size)
        counts, edges = np.histogram(raw_notes, bins=bins)
        
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

        self.max_nps = np.max(non_zero)
        self.min_nps = np.min(non_zero)
        self.mean_nps = float(np.mean(non_zero))
        self.idle_time = idle_time