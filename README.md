# BSMapInfo - Beat Saber Map Info

A small desktop utility to browse custom Beat Saber maps and inspect per-level note density (NPS) graphs and short stats. It scans a custom maps folder, parses `Info.dat` and beatmap files (v2/v3/v4 schemas), and shows levels, NPS graphs, idle time, and short statistics in a compact GUI built with CustomTkinter.

(Implemented in `BSMapInfo.py` and schema handlers.)

<p align="center">
<img width="882" height="532" alt="image" src="https://github.com/user-attachments/assets/e664f19a-1f21-4263-9eff-f5e8a85fefe2" />
</p>

## Features / UI guide

### Key interface elements
* Before using the program, select your custom maps folder. For BSManager users the path is `BSManager\BSInstances\Beat Saber\Beat Saber_Data\CustomLevels`. You can also open current BSInstances folder inside the program with `Cogwheel icon -> Open folder`.
* Browse installed custom maps on the left sidebar and select a level to view details and an NPS graph.
* You can drag and drop `.zip` map file onto:
  * the Level info frame to preview its info,
  * the Map list to add the map to your currently selected folder.

### Map selection
* `Search...` entry - Search map by: Song title, Song author, Map author.
* `Update maps` button - Checks selected folder for added/deleted songs and updates map list.
* `C` button - Clear search entry field.
* `⮟ / ⮝` button - Sort map list in ascending/descending order.
* `Song title / Song author / Map author / Song duration / BPM` selector - Sort map list by selected order.

### Program topbar / settings
* `Same-color stacks` checkbox - When enabled, stacks of the same color (e.g., two red notes stacked) are counted as a single logical note in the accuracy statistics. When disabled, each physical note is counted individually.
* `Mixed-color stacks` checbox - When enabled, opposite-color stacks (red+blue pairs) are treated as a single unit in accuracy data. When disabled, each note in such stacks is counted separately.
* `Precision step (s)` entry - Minimum value is 1. Defines the length of one precision bin in seconds. Smaller values give higher temporal resolution but increase processing time and may worsen graph readability.
* `Min idle time (s)` entry - Minimum value is 1. Defines the minimum pause length that counts toward the Idle time statistic; pauses shorter than this are treated as continuous play.
* `Update` button - Updates level info after setting were changed.
* `Change directory` button - Change your custom map folder and reload map list.
* `About` button - Shows brief info about program.

### Level information
* Difficulty buttons (color-coded) select the level difficulty and characteristic:
  * `Standard` -> `St`
  * `NoArrows` -> `NA`
  * `OneSaber` -> `OS`
  * `Lawless` -> `Ll`
  * `90Degree` -> `90D`
  * `360Degree` -> `360D`
 
The program does not detect mods other than those listed above.
 
In main level info window:
* `<Song title> by <Song author> (Mapped by <Map author>): <Level mode> <Level difficulty>` label - Main level information.
* Table of level information:
  * `BPM` - Beats per minute of the song,
  * `NPS Avg` - Average notes per second,
  * `NPS Median` - Median of the NPS distribution,
  * `NPS Max` / `NPS Min` - Maximum / minimum NPS values,
  * `NJS` - Note jump speed,
  * `Deviation` - Standard deviation of NPS (higher = more spread),
  * `Kurtosis` - A measure of tail heaviness / outliers in the NPS distribution (higher = heavy tails and a higher, sharper peak, lower = thin tails and a flatter, lower peak),
  * `Song length` - Duration of the song,
  * `Idle time` - Total time where NPS is 0 (pauses shorter than Min idle time (s) are ignored).
* `Graph` - NPS vs. time graph. You can see what parts of level harder or easier. Also you can hover mouse over graph to see exact information at given time.
 
## Run program

1. Download `BSMapInfo.exe` from [latest release page](../.././releases/latest).
2. Run `BSMapInfo.exe`

On first run the app asks you to select your custom maps folder (the folder containing each map's `Info.dat`). The app then scans that folder and populates the left sidebar.

## Troubleshooting

* **No maps listed**: Point the app at a folder containing Beat Saber custom map subfolders (each map is a directory containing an `Info.dat`). Use the `Change directory` button if the app didn’t prompt automatically. 
* **Graph shows strange values**: Maps with malformed level JSON can produce incorrect parsing; the app will show a warning for "bad mappers". 

**Known behavior / limitations**

* For some "nonstandard" maps the parser may mark `bad_mapper=True` and warn that NPS/graph might be inaccurate - this happens when the expected fields are missing or malformed.
* For v4 `Info` files the original map author field don't exist. 

## Settings & where they are stored

Settings are persisted in the Windows `%LOCALAPPDATA%\BSMapInfo\settings.json` location. The app uses that file to store:

* `target_dir` - path to your custom maps folder.
* `geometry` - window geometry.
* `bin_size` - seconds per NPS bin `Precision step` setting value (integer).
* `min_idle_time` - minimum idle time to count toward idle total.
* `merge_same_color_stacks` - See `Same-color stacks` setting.
* `merge_mixed_color_stacks` - See `Mixed-color stacks` setting.
* `sort_order` / `sort_direction` - sidebar sorting preferences.

The settings loader performs a small migration: if keys are missing they are filled with defaults and saved back. See `SettingsHandler` for details. *(Settings handling logic lives alongside the app code.)*

## Requirements

* Tested on Python 3.11.9
* Packages (installable via pip):
  * `customtkinter`
  * `tkinterdnd2`
  * `matplotlib`
  * `pillow`
  * `numpy`
  * `scipy`

## Packaging

A recommended one-file Windows build (example):

```bash
python -m PyInstaller --windowed --onefile --icon="icon.ico" BSMapInfo.py
```

You can use `.spec` file:

```bash
python -m PyInstaller BSMapInfo.spec
```

## Schema support / parsing notes

* `Info.dat` versions are detected (major version parsed from `version` or `_version`). Handlers map fields for major versions 2 and 4. See `info_schema_version_handler.py` for specifics. 
* Level/beatmap files are parsed by `level_schema_version_handler.py`, which supports level schema v2, v3 and v4 and extracts notes (beat + color). It also converts beats → seconds using song BPM and computes histograms (NPS) using NumPy. 

## License

This project is licensed under the terms of the [license](https://github.com/khivus/BSMapInfo/blob/main/LICENSE).
