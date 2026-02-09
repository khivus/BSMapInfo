import json
import numpy as np


def parse_info():
    with open("Info.dat", 'r') as file:
        info_json = json.load(file)
    
    return info_json


def get_bpm_from_info(info_json):
    info_ver = int(info_json["version"].split('.')[0])
    
    if info_ver == 2:
        return info_json["_beatsPerMinute"]
    else:
        return info_json["audio"]["bpm"]


def parse_difficulty(filename : str) -> list:
    with open(filename, 'r') as file:
        difficulty_json = json.load(file)
    
    major_ver = int(difficulty_json["version"].split('.')[0])
    notes_in_beats = []

    if major_ver == 2:
        notes_key = "_notes"
        beat_key = "_time"

        for note in difficulty_json[notes_key]:
            if note["_type"] == 3: # bomb
                continue
            notes_in_beats.append(note[beat_key])

    else:
        notes_key = "colorNotes"
        beat_key = "b"

        for note in difficulty_json[notes_key]:
            notes_in_beats.append(note[beat_key])

    return notes_in_beats


def beats_to_seconds(notes_in_beats: list, bpm: int):
    notes_in_seconds = []
    for note in notes_in_beats:
        notes_in_seconds.append((note * 60) / bpm)
    
    return notes_in_seconds


def notes_density(notes : list, bin_size : int) -> dict: # Returns list of counted notes in list
    stop = notes[len(notes) - 1] + bin_size
    bins = np.arange(0, stop, bin_size)
    counts, edges = np.histogram(notes, bins=bins)
    return dict(zip([f"{int(edges[i])}-{int(edges[i+1])}" for i in range(len(edges)-1)], counts / bin_size))


if __name__ == "__main__":
    # settings handled
    filename = "ExpertPlusStandard.dat"
    bin_size = 3

    info_json = parse_info()
    notes_in_beats = parse_difficulty(filename=filename)
    bpm = get_bpm_from_info(info_json=info_json)
    notes_in_seconds = beats_to_seconds(notes_in_beats=notes_in_beats, bpm=bpm)
    # TODO: convert notes in beats to seconds using Info.dat file 
    density = notes_density(notes=notes_in_seconds, bin_size=bin_size)

    print("Notes per second every 10 seconds:")
    for key in density.keys():
        print(f"{key}: {density[key]:.2f}")