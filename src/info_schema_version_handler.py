import json
import os


class InfoSchemaVersionHandler:

    id: int
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


    def __init__(self, map_path: str):

        self.map_path = map_path
        info_file_path = os.path.join(self.map_path, "Info.dat")
        with open(info_file_path, 'r', encoding="utf-8") as file:
            self.info_json = json.load(file)

        try:
            self.info_major_version = int(self.info_json["version"].split('.')[0])
        except:
            self.info_major_version = int(self.info_json["_version"].split('.')[0])

        if self.info_major_version == 2:
            self.v2_handler()
        else:
            self.v4_handler()

        for index, level in enumerate(self.levels):
            if level["difficulty"] == "ExpertPlus":
                self.levels[index]["difficulty"] = "Expert+"
            

    def v2_handler(self):
        self.song_title = self.info_json["_songName"]
        self.song_autor = self.info_json["_songAuthorName"]
        self.map_autor = self.info_json["_levelAuthorName"]
        self.song_duration = 0 # don't nedeed really
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
        self.song_duration = self.info_json["audio"]["songDuration"]
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
