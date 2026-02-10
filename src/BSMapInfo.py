import json
import os
import numpy as np

from info_schema_version_handler import info_schema_version_handler
from difficulty_schema_version_handler import difficulty_schema_version_handler


VERSION = "0.0.1"


def parse_file(filename: str):
    with open(filename, 'r') as file:
        data_json = json.load(file)
    
    return data_json


def beats_to_seconds(notes_in_beats: list, bpm: float):
    notes_in_seconds = []
    for note in notes_in_beats:
        notes_in_seconds.append((note * 60) / bpm)
    
    return notes_in_seconds


def notes_density(notes : list, bin_size : int, song_duration: float) -> dict: # Returns list of counted notes in list
    if not song_duration:
        stop = notes[len(notes) - 1] + bin_size
    else: 
        stop = song_duration

    bins = np.arange(0, stop, bin_size)
    counts, edges = np.histogram(notes, bins=bins)
    return dict(zip([f"{int(edges[i])}-{int(edges[i+1])}" for i in range(len(edges)-1)], counts / bin_size))


def get_short_stats(notes: dict):
    values = np.array(list(notes.values()))
    non_zero = values[values != 0]

    max_val = np.max(non_zero)
    min_val = np.min(non_zero)
    mean_val = float(np.mean(non_zero))

    return max_val, min_val, mean_val


if __name__ == "__main__":
    # settings handled
    bin_size = 3

    program_dir = os.getcwd()
    parent_dir = os.path.dirname(program_dir)
    os.chdir(parent_dir)
    target_dir = "BSMapInfo Test Maps"
    os.chdir(target_dir)
    
    for item in os.listdir():
        
        item_path = os.path.join(os.getcwd(), item)
        if not os.path.isdir(item_path):
            continue

        info_file_path = os.path.join(item_path, "Info.dat")
        info_json = parse_file(info_file_path)
        map = info_schema_version_handler(info_json)

        for map_difficulty in map.difficulties.keys():
            difficulty_file_path = os.path.join(item_path, map.difficulties[map_difficulty])
            difficulty_json = parse_file(difficulty_file_path)

            difficulty = difficulty_schema_version_handler(difficulty_json)
            difficulty.difficulty = map_difficulty
            difficulty.filename = map.difficulties[map_difficulty]
            difficulty.notes_in_seconds = beats_to_seconds(notes_in_beats=difficulty.notes_in_beats, bpm=map.bpm)
            difficulty.notes_density = notes_density(notes=difficulty.notes_in_seconds, bin_size=bin_size, song_duration=map.song_duration)
            difficulty.max_nps, difficulty.min_nps, difficulty.mean_nps = get_short_stats(notes=difficulty.notes_density)

            print(f"\n'{map.song_title}' difficulty {difficulty.difficulty}:")
            # for key in difficulty.notes_density.keys():
            #     print(f"{key}: {difficulty.notes_density[key]:.2f}")
            print(f"NPS: max = {difficulty.max_nps:.2f}, min = {difficulty.min_nps:.2f}, mean = {difficulty.mean_nps:.2f}")
