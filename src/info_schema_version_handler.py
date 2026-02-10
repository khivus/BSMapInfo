class info_schema_version_handler():

    info_major_version: int
    song_title: str
    song_duration: float
    bpm: float
    added_date: str
    difficulties: dict


    def __init__(self, info_json):
        self.info_json = info_json
        
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

        difficulties = {}
        for characteristic in self.info_json["_difficultyBeatmapSets"]:
            for difficulty in characteristic["_difficultyBeatmaps"]:
                difficulties[difficulty["_difficulty"]] = difficulty["_beatmapFilename"]
        
        self.difficulties = difficulties


    def v4_handler(self):
        self.song_title = self.info_json["song"]["title"]
        self.song_duration = self.info_json["audio"]["songDuration"]
        self.bpm = self.info_json["audio"]["bpm"]

        difficulties = {}
        for difficulty in self.info_json["difficultyBeatmaps"]:
            difficulties[difficulty["difficulty"]] = difficulty["beatmapDataFilename"]
        
        self.difficulties = difficulties
