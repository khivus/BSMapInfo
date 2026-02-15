# BSMapInfo — Beat Saber Map Info

A small desktop utility to browse custom Beat Saber maps and inspect per-level note density (NPS) graphs and short stats. It scans a custom maps folder, parses `Info.dat` and beatmap files (v2/v3/v4 schemas), and shows levels, NPS graphs, idle time, and short statistics in a compact GUI built with CustomTkinter. Beat Saber
(Implemented in `BSMapInfo.py` and schema handlers.) 

---

## Features

* Browse installed custom maps and select a level to view details and an NPS graph. 
* Supports multiple `Info`/level schema versions (v2, v3, v4).  
* Configurable bin size (seconds) for NPS calculation and minimum idle time detection. 
* Toggle options:
  * Count stacked notes (notes at the same beat)
  * Count different-color notes at same beat
* Shows mean/max/min NPS and total idle time per level. 

---

## Using the UI (short)

* Left sidebar: list of maps (cover + basic info). Click a map to expand and view levels. 
* Top bar controls:

  * Toggle stacked/different-color counting
  * Bin size (seconds) entry
  * Min idle time (seconds) entry
  * Update button (recalculate for current level)
* Level view: NPS graph, mean/max/min NPS, total idle time, and a list of detected idle segments. 

---

## Requirements

* Python 3.8+
* Packages (installable via pip):

  * `customtkinter`
  * `matplotlib`
  * `pillow`
  * `numpy`

---

## Install & Run

1. Clone the repo (or copy the project files) to a folder.
2. Run the app:

```bash
python BSMapInfo.py
```

When the app first starts it will ask you to select your custom maps folder (the folder that contains individual map directories). The app then scans that folder and populates the left sidebar. 

---

## Packaging

A recommended one-file Windows build (example):

```bash
python -m PyInstaller --windowed --onefile --icon="icon.ico" BSMapInfo.py
```

(There is a commented example in `BSMapInfo.py` — adjust paths and icon as needed.) 

---

## Settings & where they are stored

Settings are persisted in the Windows `%LOCALAPPDATA%\BSMapInfo\settings.json` location. The app uses that file to store:

* `target_dir` — path to your custom maps folder
* `geometry` — window geometry
* `bin_size` — seconds per NPS bin (integer)
* `min_idle_time` — minimum idle time to count toward idle total
* `stacked_counted` — boolean: count stacked notes
* `different_color_counted` — boolean: count different-color occurrences at same beat
* `sort_order` / `sort_direction` — sidebar sorting preferences

The settings loader performs a small migration: if keys are missing they are filled with defaults and saved back. See `SettingsHandler` for details. *(Settings handling logic lives alongside the app code.)*

---

## Schema support / parsing notes

* `Info.dat` versions are detected (major version parsed from `version` or `_version`). Handlers map fields for major versions 2 and 4. See `info_schema_version_handler.py` for specifics. 
* Level/beatmap files are parsed by `level_schema_version_handler.py`, which supports level schema v2, v3 and v4 and extracts notes (beat + color). It also converts beats → seconds using song BPM and computes histograms (NPS) using NumPy. 

**Known behavior / limitations**

* For some “nonstandard” maps the parser may mark `bad_mapper=True` and warn that NPS/graph might be inaccurate — this happens when the expected fields are missing or malformed. 
* For v4 `Info` files the original map author field may be empty (behavior depends on map metadata). 

---

## Troubleshooting

* **App crashes on startup**: Ensure `customtkinter`, `matplotlib`, `pillow`, `numpy` are installed and you run on Python 3.8+.
* **No maps listed**: Point the app at a folder containing Beat Saber custom map subfolders (each map is a directory containing an `Info.dat`). Use the `Change directory` button if the app didn’t prompt automatically. 
* **Graph shows strange values**: Maps with malformed level JSON can produce incorrect parsing; the app will show a warning for “bad mappers.” 

---

## License

This project is licensed under the terms of the [license](https://github.com/khivus/BSMapInfo/blob/main/LICENSE).
