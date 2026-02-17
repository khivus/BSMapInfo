import json
import os
import mutagen


class MapHandler:

    info_major_version: int
    map_path: str
    song_title: str
    song_autor: str
    map_autor: str
    song_duration: float
    bpm: float
    cover_image_filename: str
    levels: list

    characteristics = {
        "Standard" : "St",
        "NoArrows" : "NA",
        "OneSaber" : "OS",
        "Lawless" : "Ll",
        "90Degree" : "90D",
        "360Degree" : "360D"
    }

    difficulties = {
        "Easy" : 1,
        "Normal" : 3,
        "Hard" : 5,
        "Expert" : 7,
        "Expert+" : 9
    }


    def __init__(self, map_path):

        self.map_path = map_path
        info_file_path = os.path.join(self.map_path, "Info.dat")

        try:
            with open(info_file_path, 'r', encoding="utf-8") as file:
                self.info_json = json.load(file)
        except:
            self.info_json = {}
            return

        try:
            self.info_major_version = int(self.info_json["_version"].split('.')[0])
        except:
            self.info_major_version = int(self.info_json["version"].split('.')[0])

        if self.info_major_version == 2:
            self.v2_handler()
        else:
            self.v4_handler()

        self._check_bpm_regions()

        for index, level in enumerate(self.levels):
            if level["difficulty"] == "ExpertPlus":
                self.levels[index]["difficulty"] = "Expert+"
            

    def v2_handler(self):
        self.song_title = self.info_json["_songName"]
        self.song_autor = self.info_json["_songAuthorName"]
        self.map_autor = self.info_json["_levelAuthorName"]
        self.song_duration = self._get_song_length()
        self.bpm = self.info_json["_beatsPerMinute"]
        self.cover_image_filename = self.info_json["_coverImageFilename"]

        levels = []
        for characteristic in self.info_json["_difficultyBeatmapSets"]:
            if characteristic["_beatmapCharacteristicName"] not in self.characteristics.keys():
                continue

            for level in characteristic["_difficultyBeatmaps"]:
                levels.append({
                    "characteristic" : characteristic["_beatmapCharacteristicName"],
                    "difficulty" : level["_difficulty"],
                    "njs" : level["_noteJumpMovementSpeed"],
                    "filename" : level["_beatmapFilename"]
                })
        
        self.levels = levels


    def v4_handler(self):
        self.song_title = self.info_json["song"]["title"]
        self.song_autor = self.info_json["song"]["author"]
        self.map_autor = "" # Very good development team
        self.song_duration = self.info_json["audio"]["songDuration"] if self.info_json["audio"]["songDuration"] else self._get_song_length()
        self.bpm = self.info_json["audio"]["bpm"]
        self.cover_image_filename = self.info_json["coverImageFilename"]

        levels = []
        for level in self.info_json["difficultyBeatmaps"]:
            if level["characteristic"] not in self.characteristics.keys():
                continue

            levels.append({
                "characteristic" : level["characteristic"],
                "difficulty" : level["difficulty"],
                "njs" : level["noteJumpMovementSpeed"],
                "filename" : level["beatmapDataFilename"]
            })
        
        self.levels = levels


    def _get_song_length(self):
        if self.info_major_version == 2:
            path = os.path.join(self.map_path, self.info_json["_songFilename"])
        else:
            path = os.path.join(self.map_path, self.info_json["audio"]["songFilename"])

        audio = mutagen.File(path) # type: ignore
        if audio is None or not hasattr(audio, "info"):
            return 0
        return audio.info.length
    

    def _check_bpm_regions(self):
        self.sample_count = 0
        self.bpm_regions = []

        audio_info = ("BPMInfo.dat", "AudioData.dat")
        for file_name in audio_info:
            audio_info_file_path = os.path.join(self.map_path, file_name)
            if not os.path.isfile(audio_info_file_path):
                continue

            with open(audio_info_file_path, 'r', encoding="utf-8") as file:
                audio_info = json.load(file)
            
            try:
                audio_info_version = int(audio_info["_version"].split('.')[0])
            except:
                audio_info_version = int(audio_info["version"].split('.')[0])

            bpm_regions = []

            if audio_info_version == 2:
                self.sample_count = audio_info["_songSampleCount"]

                for region in audio_info["_regions"]:
                    bpm_regions.append({
                        "start_sample_index" : region["_startSampleIndex"],
                        "end_sample_index" : region["_endSampleIndex"],
                        "start_beat" : region["_startBeat"],
                        "end_beat" : region["_endBeat"]
                    })
            else:
                self.sample_count = audio_info["songSampleCount"]

                for region in audio_info["bpmData"]:
                    bpm_regions.append({
                        "start_sample_index" : region["si"],
                        "end_sample_index" : region["ei"],
                        "start_beat" : region["sb"],
                        "end_beat" : region["eb"]
                    })

            self.bpm_regions = bpm_regions