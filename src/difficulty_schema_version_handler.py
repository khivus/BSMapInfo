class difficulty_schema_version_handler():
    
    difficulty_major_version: int
    difficulty: str
    filename: str
    notes_in_beats: list
    notes_in_seconds: list
    notes_density: dict
    max_nps: float
    min_nps: float
    mean_nps: float


    def __init__(self, difficulty_json):
        self.difficulty_json = difficulty_json
        try:
            self.difficulty_major_version = int(self.difficulty_json["version"].split('.')[0])
        except:
            self.difficulty_major_version = int(self.difficulty_json["_version"].split('.')[0])

        if self.difficulty_major_version == 2:
            self.v2_handler()
        elif self.difficulty_major_version == 3:
            self.v3_handler()
        else:
            self.v4_handler()


    def v2_handler(self):
        notes = []
        for note in self.difficulty_json["_notes"]:
            if note["_type"] == 3: # bomb
                continue
            notes.append(note["_time"])

        self.notes_in_beats = notes

        # note colors later
        # self.note_color = self.difficulty_json["_notes"]["_type"]


    def v3_handler(self):
        notes = []
        for note in self.difficulty_json["colorNotes"]:
            notes.append(note["b"])
        
        self.notes_in_beats = notes

        # self.note_color = self.difficulty_json["colorNotes"]["c"]


    def v4_handler(self):
        notes = []
        for note in self.difficulty_json["colorNotes"]:
            notes.append(note["b"])

        self.notes_in_beats = notes

        # self.note_color = self.difficulty_json["colorNotesData"]["c"]