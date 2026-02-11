import json


class InfoSchemaVersionHandler():

    info_major_version: int
    song_title: str
    song_duration: float
    bpm: float
    added_date: str
    levels: list

    characteristics = [
        "Standard",
        "NoArrows",
        "OneSaber",
        "360Degree",
        "90Degree"
    ]


    def __init__(self, filepath: str):

        with open(filepath, 'r', encoding="utf-8") as file:
            self.info_json = json.load(file)

        try:
            self.info_major_version = int(self.info_json["version"].split('.')[0])
        except:
            self.info_major_version = int(self.info_json["_version"].split('.')[0])

        self.added_date = "addedDate" # need to be handled later

        if self.info_major_version == 2:
            self.v2_handler()
        else:
            self.v4_handler()
            

    def v2_handler(self):
        self.song_title = self.info_json["_songName"]
        self.song_duration = 0 # don't nedeed really
        self.bpm = self.info_json["_beatsPerMinute"]

        levels = []
        for characteristic in self.info_json["_difficultyBeatmapSets"]:
            if characteristic["_beatmapCharacteristicName"] not in self.characteristics:
                continue

            for level in characteristic["_difficultyBeatmaps"]:
                levels.append({
                    "characteristic" : characteristic["_beatmapCharacteristicName"],
                    "difficulty" : level["_difficulty"],
                    "filename" : level["_beatmapFilename"]
                })
        
        self.levels = levels


    def v4_handler(self):
        self.song_title = self.info_json["song"]["title"]
        self.song_duration = self.info_json["audio"]["songDuration"]
        self.bpm = self.info_json["audio"]["bpm"]

        levels = []
        for level in self.info_json["difficultyBeatmaps"]:
            if level["characteristic"] not in self.characteristics:
                continue

            levels.append({
                "characteristic" : level["characteristic"],
                "difficulty" : level["difficulty"],
                "filename" : level["beatmapDataFilename"]
            })
        
        self.levels = levels
