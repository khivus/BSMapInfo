import os
import sys
import zipfile
import shutil

import customtkinter as ctk
import matplotlib.pyplot as plt

from pathlib import Path
from tkinterdnd2 import DND_FILES, TkinterDnD
from PIL import Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from settings_handler import SettingsHandler
from map_handler import MapHandler
from level_handler import LevelHandler


VERSION = "1.1.1"
AUTHOR = "Khivus"
APP_NAME = "BSMapInfo"
FULL_APP_NAME = "Beat Saber Map Info"


# python -m PyInstaller --windowed --onefile --icon="icon.ico" src/BSMapInfo.py

# TODO: Tooltips
# TODO: Update README


class BSMapInfoApp(ctk.CTk, TkinterDnD.DnDWrapper):
    
    def __init__(self) -> None:
        super().__init__()
        self.TkdndVersion = TkinterDnD._require(self)

        ctk.set_appearance_mode("dark")
        self.title(FULL_APP_NAME)
        self.iconbitmap(sys.executable)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.set_state()

        self.geometry(self.settings.geometry)
        self.minsize(880, 500)

        self.build_ui()

        if self.settings.target_dir:
            self.load_map_list()


    def set_state(self):
        self.last_active_sidebar_btn_index = -1
        self.last_active_levels_btn_index = -1
        self.is_map_btn_locked = False
        self.maps = []
        self.maps_indices = []

        self.order_variants = {
            "Song title" : "song_title",
            "Song autor" : "song_autor",
            "Map autor" : "map_autor",
            "Song duration" : "song_duration",
            "BPM" : "bpm"
        }
        self.direction_variants = ["⮟", "⮝"]

        self.padding = 5
        self.button_colors = {
            "default" : "#333333",
            "Easy" : "#008055",
            "Normal" : "#1268A1",
            "Hard" : "#bd5500",
            "Expert" : "#b52a1c",
            "Expert+" : "#7646af"
        }
        self.button_hover_colors = {
            "default" : "#4d4d4d",
            "Easy" : "#004d32",
            "Normal" : "#0c476e",
            "Hard" : "#8a3e00",
            "Expert" : "#821e14",
            "Expert+" : "#54327d"
        }

        self.search_var = ctk.StringVar(value="Search...")
        
        self.settings = SettingsHandler(self, APP_NAME)


    def build_ui(self):
        # Frames
        # Topbar frame
        self.topbar = ctk.CTkFrame(self, height=40)
        self.topbar.grid(row=0, column=0, sticky="nsew", pady=self.padding)

        # Main frame
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.grid(row=1, column=0, sticky="nsew")

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Sidebar frame
        self.sidebar = ctk.CTkFrame(self.main_frame, width=232)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Topsidebar frame
        self.topsidebar = ctk.CTkFrame(self.sidebar, width=222)
        self.topsidebar.grid(row=0, column=0, sticky="nsew", pady=self.padding, padx=self.padding)

        # Search frame
        self.search_frame = ctk.CTkFrame(self.topsidebar, height=38, fg_color="#2b2b2b")
        self.search_frame.grid(row=0, column=0, sticky="nsew")

        # Sort frame
        self.sort_frame = ctk.CTkFrame(self.topsidebar, height=38, fg_color="#2b2b2b")
        self.sort_frame.grid(row=1, column=0, sticky="nsew")

        # Maps list frame
        self.maps_list_frame = ctk.CTkScrollableFrame(self.sidebar)
        self.maps_list_frame.grid(row=2, column=0, sticky="nsew", pady=self.padding, padx=self.padding)
        self.sidebar.grid_rowconfigure(2, weight=1)

        # Graph frame
        self.map_info_frame = ctk.CTkFrame(self.main_frame)
        self.map_info_frame.grid(row=0,column=1, sticky="nsew")

        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Levels frame
        self.levels_frame = ctk.CTkFrame(self.map_info_frame, height=38)
        self.levels_frame.grid(row=0,column=0, sticky="nsew", pady=self.padding, padx=self.padding)

        # Level info frame
        self.level_info_frame = ctk.CTkFrame(self.map_info_frame)
        self.level_info_frame.grid(row=1,column=0, sticky="nsew", pady=self.padding, padx=self.padding)

        self.map_info_frame.grid_columnconfigure(0, weight=1)
        self.map_info_frame.grid_rowconfigure(1, weight=1)

        # Topbar items
        self.same_color_lbl = ctk.CTkLabel(self.topbar, text="Same-color stacks")
        self.same_color_lbl.pack(side="left", padx=self.padding)
        self.same_color_cb = ctk.CTkCheckBox(self.topbar, text="", width=0, variable=self.settings.merge_same_color_stacks, hover_color=self.button_hover_colors["default"], fg_color=self.button_hover_colors["default"], checkmark_color="white")
        self.same_color_cb.pack(side="left")

        self.different_color_lbl = ctk.CTkLabel(self.topbar, text="Mixed-color stacks")
        self.different_color_lbl.pack(side="left", padx=self.padding)
        self.different_color_cb = ctk.CTkCheckBox(self.topbar, text="", width=0, variable=self.settings.merge_mixed_color_stacks, hover_color=self.button_hover_colors["default"], fg_color=self.button_hover_colors["default"], checkmark_color="white")
        self.different_color_cb.pack(side="left")

        self.bin_size_label = ctk.CTkLabel(self.topbar, text="Precision step (s)")
        self.bin_size_label.pack(side="left", padx=self.padding)
        self.bin_size_entry = ctk.CTkEntry(self.topbar, width=50, placeholder_text="3")
        self.bin_size_entry.insert(0, f"{self.settings.bin_size}")
        self.bin_size_entry.pack(side="left", padx=self.padding)
        self.bin_size_entry.bind("<Key>", self.validate_only_digits)

        self.min_idle_time_label = ctk.CTkLabel(self.topbar, text="Min idle time (s)")
        self.min_idle_time_label.pack(side="left", padx=self.padding)
        self.min_idle_time_entry = ctk.CTkEntry(self.topbar, width=50, placeholder_text="3")
        self.min_idle_time_entry.insert(0, f"{self.settings.min_idle_time}")
        self.min_idle_time_entry.pack(side="left", padx=self.padding)
        self.min_idle_time_entry.bind("<Key>", self.validate_only_digits)

        self.update_btn = ctk.CTkButton(self.topbar, text="Update", width=50, fg_color=self.button_colors["default"], hover_color=self.button_hover_colors["default"], command=self.update_level_info)
        self.update_btn.pack(side="left", padx=self.padding)

        self.change_dir_btn = ctk.CTkButton(self.topbar, text="Change directory", width=80, fg_color=self.button_colors["default"], hover_color=self.button_hover_colors["default"], command=lambda: self.change_target_dir(forced=True))
        self.change_dir_btn.pack(side="left", padx=self.padding)

        self.about_btn = ctk.CTkButton(self.topbar, text="About", width=25, fg_color=self.button_colors["default"], hover_color=self.button_hover_colors["default"], command=lambda: self.show_on_top_window(f"{FULL_APP_NAME}\nVersion {VERSION}\nBy: {AUTHOR}"))
        self.about_btn.pack(side="left", padx=self.padding)

        # Search items
        self.search_entry = ctk.CTkEntry(self.search_frame, width=112, textvariable=self.search_var)
        self.search_entry.grid(row=0, column=0, padx=self.padding, pady=self.padding)
        self.search_var.trace_add("write", self.filter_sidebar)

        self.update_map_list_btn = ctk.CTkButton(self.search_frame, width=90, text="Update maps", fg_color=self.button_colors["default"], hover_color=self.button_hover_colors["default"], command=self.update_map_list)
        self.update_map_list_btn.grid(row=0, column=1, padx=self.padding, pady=self.padding)

        # Sort items
        self.sort_direction = ctk.CTkButton(self.sort_frame, width=28, fg_color=self.button_colors["default"], hover_color=self.button_hover_colors["default"], text=self.direction_variants[self.settings.sort_direction], command=self.sort_direction_change)
        self.sort_direction.grid(row=0, column=0, padx=self.padding, pady=self.padding)

        variable = ctk.StringVar()
        for key, value in self.order_variants.items():
            if value == self.settings.sort_order:
                variable.set(key)

        self.sort_order = ctk.CTkOptionMenu(self.sort_frame, width=174, fg_color=self.button_colors["default"], button_color=self.button_colors["default"], button_hover_color=self.button_hover_colors["default"], values=list(self.order_variants.keys()), variable=variable, command=self.sort_order_callback)
        self.sort_order.grid(row=0, column=1, padx=self.padding, pady=self.padding)

        # Drag and drop to add song to map dir
        self.sidebar.drop_target_register(DND_FILES) # type: ignore
        self.sidebar.dnd_bind('<<Drop>>', self.drop_add_file) # type: ignore

        # Drag and drop zips on level info frame
        self.map_info_frame.drop_target_register(DND_FILES) # type: ignore
        self.map_info_frame.dnd_bind('<<Drop>>', self.drop) # type: ignore

        start_info_label = ctk.CTkLabel(self.level_info_frame, text="Select map on the left sidebar to see info about it.")
        start_info_label.cget("font").configure(size=20)
        start_info_label.pack(padx=self.padding * 2, pady=self.padding, anchor="w")

        dnd_label = ctk.CTkLabel(self.level_info_frame, text="You can drag and drop any map .zip\non this frame to show it info at any time!\nAnd drop on map list to add song to a map folder!")
        dnd_label.cget("font").configure(size=26)
        dnd_label.pack(expand=True)


    def on_closing(self):
        self.settings.geometry = self.geometry()
        self.settings.save_settings()
        plt.close('all')
        app.quit()
        app.destroy()


    def change_target_dir(self, forced = False):
        if self.settings.target_dir and not forced:
            return
    
        selected_dir = ctk.filedialog.askdirectory(title="Select custom maps folder")

        if not selected_dir and not self.settings.target_dir:
            no_dir_label = ctk.CTkLabel(self.level_info_frame, text="Please select custom maps folder using \"Change directory\" button.")
            no_dir_label.pack(padx=self.padding * 2, anchor="w")
            self.update()
            return
        elif not selected_dir or selected_dir == self.settings.target_dir:
            return

        self.settings.target_dir = selected_dir
        self.reload_map_list()


    def reload_map_list(self):
        self.clear_frame(self.maps_list_frame)
        self.clear_frame(self.levels_frame)
        self.clear_frame(self.level_info_frame)
        self.last_active_sidebar_btn_index = -1
        self.last_active_levels_btn_index = -1
        self.maps = []
        self.maps_indices = []

        self.progress_bar_label = ctk.CTkLabel(self.level_info_frame, text="Loading maps (0/0)...")
        self.progress_bar = ctk.CTkProgressBar(self.level_info_frame)

        self.load_map_list(True)


    def validate_only_digits(self, event):
        entry = event.widget
        old_value = entry.get()
        new_value = old_value + event.char

        if new_value == "" or new_value.isdigit():
            return

        if event.keysym == "BackSpace" or event.keysym == "Delete":
            return

        return "break"


    def update_level_info(self, *args):
        try:
            bin_size = int(self.bin_size_entry.get())
        except:
            bin_size = 0

        if bin_size < 1:
            self.bin_size_entry.delete(0, ctk.END)
            self.bin_size_entry.insert(0, f"{self.settings.bin_size}")
            return

        try:
            min_idle_time = int(self.min_idle_time_entry.get())
        except:
            min_idle_time = 0

        if min_idle_time < 1:
            self.min_idle_time_entry.delete(0, ctk.END)
            self.min_idle_time_entry.insert(0, f"{self.settings.min_idle_time}")
            return

        self.settings.bin_size = bin_size
        self.settings.min_idle_time = min_idle_time
        if self.last_active_sidebar_btn_index != -1 and self.last_active_levels_btn_index != -1:
            self.unload_level(map_index=self.last_active_sidebar_btn_index, level_index=self.last_active_levels_btn_index, forced=True)


    def drop_add_file(self, event):
        file_path = event.data.strip("{}")
        new_dir_name = Path(file_path).stem
        new_dir_path = Path(self.settings.target_dir) / new_dir_name

        try:
            with zipfile.ZipFile(file_path, 'r') as archive:
                new_dir_path.mkdir(parents=True, exist_ok=True)
                archive.extractall(new_dir_path)
            
            self.update_map_list()

        except:
            self.show_on_top_window("You can add only archives!")


    def drop(self, event):
        file_path = event.data.strip("{}")

        temp_map_dir = self.settings.app_dir / "temp_map"
        if os.path.isdir(temp_map_dir):
            shutil.rmtree(temp_map_dir)
        temp_map_dir.mkdir(parents=True, exist_ok=True)

        try:
            with zipfile.ZipFile(file_path, 'r') as archive:
                archive.extractall(temp_map_dir)
            
            self.unload_map(index=-1, custom_dir=temp_map_dir)

        except:
            self.show_on_top_window("You can add only archives!")


    def show_on_top_window(self, text: str):
        splitted = text.split("\n")
        max_row_len = 0
        for row in splitted:
            if max_row_len < len(row):
                max_row_len = len(row)

        on_top_win = ctk.CTkToplevel(self)
        on_top_win.geometry(f"{max_row_len * 8}x{80 + (15 * len(splitted))}")
        on_top_win.resizable(False, False)
        on_top_win.title(f"{APP_NAME}")
        
        on_top_win.transient(self)
        on_top_win.grab_set()

        on_top_win.update_idletasks()
        x = self.winfo_x() + ((self.winfo_width() - on_top_win.winfo_width()) // 2)
        y = self.winfo_y() + ((self.winfo_height() - on_top_win.winfo_height()) // 2)
        on_top_win.geometry(f"+{x}+{y}")

        label = ctk.CTkLabel(on_top_win, text=text, justify="center")
        label.pack(expand=True, pady=self.padding)

        close_btn = ctk.CTkButton(on_top_win, fg_color=self.button_colors["default"], hover_color=self.button_hover_colors["default"], text="Ok", command=on_top_win.destroy)
        close_btn.pack(pady=self.padding)


    def filter_sidebar(self, *args):
        query = self.search_var.get().lower()
        for index in self.maps_indices:
            if query in self.maps[index]["map"].song_title.lower() or query in self.maps[index]["map"].song_autor.lower() or query in self.maps[index]["map"].map_autor.lower():
                self.maps[index]["btn"].pack_forget()
                self.maps[index]["btn"].pack(pady=5, fill="x")
            else:
                self.maps[index]["btn"].pack_forget()
        self.maps_list_frame._parent_canvas.yview_moveto(0)


    def sort_direction_change(self):
        self.settings.sort_direction = not self.settings.sort_direction
        self.sort_direction.configure(text=self.direction_variants[self.settings.sort_direction])
        self.sort_map_list()


    def sort_order_callback(self, choise):
        self.settings.sort_order = self.order_variants[choise]
        self.sort_map_list()


    def update_map_list(self):
        old_map_list = set(self.list_dir)
        new_list_dir = os.listdir()
        new_map_list = set(new_list_dir)

        removed_maps = old_map_list - new_map_list
        new_maps = new_map_list - old_map_list

        if not removed_maps and not new_maps:
            return

        self.list_dir = new_list_dir

        if removed_maps:
            self.reload_map_list()

        if new_maps:
            for item in new_maps:
                new_index = max(self.maps_indices) + 1
                self.add_map_to_list(new_index, item)

            self.sort_map_list()


    def load_map_list(self, progress_bar_enabled = False):
        if progress_bar_enabled:
            self.progress_bar_label.pack(padx=self.padding * 2, pady=self.padding, anchor="w")
            self.progress_bar.pack(padx=self.padding * 2, fill="x")
            self.progress_bar.set(0)
            self.progress_bar.start()
            self.update()

        os.chdir(self.settings.target_dir)
        self.list_dir = os.listdir()
        list_dir_len = len(self.list_dir)
        update_ticks = int(list_dir_len / 5)

        for index, item in enumerate(self.list_dir):
            returned = self.add_map_to_list(index, item)
            
            if returned == -1:
                break

            if progress_bar_enabled and not index % update_ticks:
                self.progress_bar.set(index / list_dir_len)
                self.progress_bar_label.configure(text=f"Loading maps ({index}/{list_dir_len})...")
                self.update()

        self.sort_map_list()

        if progress_bar_enabled:
            self.progress_bar.stop()
            self.progress_bar_label.pack_forget()
            self.progress_bar.pack_forget()


    def add_map_to_list(self, index, item):
        dir_path = os.path.join(os.getcwd(), item)
        if not os.path.isdir(dir_path):
            return

        map = MapHandler(map_path=dir_path)

        if not map.info_json:
            self.after(500, lambda: self.show_on_top_window(f"Can't find 'Info.dat' in folder:\n{dir_path}\nDelete this folder or return correct info file back!"))
            return -1

        map_btn_frame = ctk.CTkFrame(self.maps_list_frame, height=50, fg_color=self.button_colors["default"])

        map_image_path = os.path.join(map.map_path, map.cover_image_filename)
        orig_map_image = Image.open(map_image_path)
        map_image = ctk.CTkImage(light_image=orig_map_image, size=(40, 40))

        map_image_label = ctk.CTkLabel(map_btn_frame, image=map_image, text="")
        map_image_label.grid(row=0, column=0, padx=self.padding, pady=self.padding, sticky="n")

        map_info = f"{map.song_title}\n"
        map_info += f"By: {map.song_autor}\n" if map.song_autor else ""
        map_info += f"Map by: {map.map_autor}" if map.map_autor else ""

        map_info_label = ctk.CTkLabel(map_btn_frame, text=map_info, wraplength=150, justify="left")
        map_info_label.grid(row=0, column=1, pady=self.padding, sticky="nw")

        self.bind_all_children(map_btn_frame, index)

        self.maps.append({"map" : map, "btn" : map_btn_frame})
        self.maps_indices.append(index)


    def sort_map_list(self):
        order = self.settings.sort_order
        
        if order == "song_title":
            self.maps_indices.sort(key=lambda i: self.maps[i]["map"].song_title)
        elif order == "song_autor":
            self.maps_indices.sort(key=lambda i: self.maps[i]["map"].song_autor)
        elif order == "map_autor":
            self.maps_indices.sort(key=lambda i: self.maps[i]["map"].map_autor)
        elif order == "song_duration":
            self.maps_indices.sort(key=lambda i: self.maps[i]["map"].song_duration)
        elif order == "bpm":
            self.maps_indices.sort(key=lambda i: self.maps[i]["map"].bpm)

        if self.settings.sort_direction:
            self.maps_indices.reverse()

        for item in self.maps:
            item["btn"].pack_forget()

        for index in self.maps_indices:
            map_btn_frame = self.maps[index]["btn"]
            map_btn_frame.pack(pady=5, fill="x")
            map_btn_frame.pack_propagate(False)


    def bind_all_children(self, parent, index):

        parent.bind("<Button-1>", lambda event, i=index : self.unload_map(i))
        parent.bind("<Enter>", lambda event, i=index : self.on_enter(i))
        parent.bind("<Leave>", lambda event, i=index : self.on_leave(i))

        for child in parent.winfo_children():
            self.bind_all_children(child, index)


    def on_enter(self, index): 
        self.maps[index]["btn"].configure(fg_color=self.button_hover_colors["default"])


    def on_leave(self, index, forced = False):
        if self.last_active_sidebar_btn_index != index or forced:
            self.maps[index]["btn"].configure(fg_color=self.button_colors["default"])


    def unlock_btn(self): # Button spam protection
        self.is_map_btn_locked = False


    def unload_map(self, index: int, custom_dir = None):
        if (self.last_active_sidebar_btn_index == index or self.is_map_btn_locked) and not custom_dir:
            return

        # lock button for spam protection
        self.is_map_btn_locked = True
        self.after(250, self.unlock_btn)

        # Clear frames
        self.clear_frame(self.levels_frame)
        self.clear_frame(self.level_info_frame)

        # Clear previous button selector
        if self.last_active_sidebar_btn_index != -1:
            self.on_leave(self.last_active_sidebar_btn_index, True)

        # Clear level button index
        self.last_active_levels_btn_index = -1

        self.levels_frame.update_idletasks()
        self.level_info_frame.update_idletasks()

        self.after(20, lambda: self.load_map(index, custom_dir))


    def load_map(self, index: int, custom_dir = None):

        if not custom_dir:
            # Set active color for selected button
            self.on_enter(index)
            map: MapHandler = self.maps[index]["map"]

        else:
            map = MapHandler(map_path=custom_dir)
            self.temp_map = map

        self.map_levels = []
        max_difficulty_index = 0
        max_difficulty = 0
        i = 0

        for i, level in enumerate(map.levels):
            lvl_btn = ctk.CTkButton(
                self.levels_frame, 
                text=f"{map.characteristics[level['characteristic']]} {level['difficulty']}",
                command=lambda li=i : self.unload_level(map_index=index, level_index=li, custom_dir=custom_dir),
                fg_color=self.button_colors[level['difficulty']],
                hover_color=self.button_hover_colors[level['difficulty']]
            )
            lvl_btn.grid(row=i // 6, column=i % 6, padx=self.padding, pady=self.padding, sticky="ew")
            self.levels_frame.grid_columnconfigure(i, weight=1)
            self.map_levels.append({"level" : level, "btn" : lvl_btn})

            if max_difficulty <= map.difficulties[level["difficulty"]] and level["characteristic"] == "Standard":
                max_difficulty = map.difficulties[level["difficulty"]]
                max_difficulty_index = i

        if max_difficulty == 0:
            max_difficulty_index = i

        self.last_active_sidebar_btn_index = index

        self.unload_level(map_index=index, level_index=max_difficulty_index, custom_dir=custom_dir)
        

    def clear_frame(self, frame: ctk.CTkFrame | ctk.CTkScrollableFrame):
        for widget in frame.winfo_children():
            widget.destroy()
        frame.update_idletasks()


    def unload_level(self, map_index: int, level_index: int, forced = False, custom_dir = None):
        if self.last_active_levels_btn_index == level_index and not forced:
            return
        
        # Clear frames
        self.clear_frame(self.level_info_frame)
        plt.close('all')

        # Clear last button active
        if self.last_active_levels_btn_index != -1:
            self.map_levels[self.last_active_levels_btn_index]["btn"].configure(fg_color=self.button_colors[self.map_levels[self.last_active_levels_btn_index]["level"]["difficulty"]], border_width=0)

        self.level_info_frame.update_idletasks()

        self.level_info_frame.after(10, lambda: self.load_level(map_index=map_index, level_index=level_index, custom_dir=custom_dir))


    def load_level(self, map_index: int, level_index: int, custom_dir = None):
        if not custom_dir:
            map: MapHandler = self.maps[map_index]["map"]
        else:
            map = self.temp_map

        level = LevelHandler(map=map, settings=self.settings, level_index=level_index)

        if not level.level_json:
            self.show_on_top_window("Level file dissapeared!\nUpdate maps list if you deleted map!")
            return

        # Set active button color
        self.map_levels[level_index]["btn"].configure(fg_color=self.button_hover_colors[level.difficulty], border_width=1, border_color="white")

        # Set level in label
        map_name_text = f"{map.song_title}"
        map_name_text += f" by {map.song_autor}" if map.song_autor else ""
        map_name_text += f" (Mapped by {map.map_autor})" if map.map_autor and len(map_name_text) < 45 else "" # If name is too long just don't print mappers names
        map_name_text += f": {level.characteristic} {level.difficulty}"

        self.map_name = ctk.CTkLabel(self.level_info_frame, text=map_name_text)
        self.map_name.grid(row=0, column=0, padx=self.padding * 2, sticky="w")

        self.last_active_levels_btn_index = level_index

        if not level.notes_in_beats:
            error_text = "Can't find notes in map!"
            self.error_label = ctk.CTkLabel(self.level_info_frame, text=error_text)
            self.error_label.grid(row=1, column=0, padx=self.padding * 2, sticky="w")
            return
        
        song_duration = level.time_adjust(map.song_duration if map.song_duration else level.notes_density[len(level.notes_density) - 1]['end'])

        info = {
            "BPM" : map.bpm,
            "NPS Avg" : level.mean_nps,
            "NPS Median" : level.median,
            "NPS Max" : level.max_nps,
            "NPS Min" : level.min_nps,
            "NJS" : level.njs,
            "Deviation" : level.standard_deviation,
            "Kurtosis" : level.kurtosis,
            "Song Length" : song_duration,
            "Idle Time" : level.idle_time,
        }

        info_table_frame = ctk.CTkFrame(self.level_info_frame, fg_color="#2b2b2b")
        info_table_frame.grid(row=1, column=0, padx=7, sticky="ew")

        for index, key in enumerate(info.keys()):
            item_frame = ctk.CTkFrame(info_table_frame, border_width=2, border_color=self.button_hover_colors["default"])
            item_frame.grid(row=0, column=index)

            info_text = ctk.CTkLabel(item_frame, text=key, height=18)
            info_text.pack(padx=3, pady=2)

            if key not in ("Song Length", "Idle Time"):
                text_value = round(info[key], 2)
            else:
                text_value = ""
                text_value += f"{info[key][0]} m " if info[key][0] else ""
                text_value += f"{info[key][1]} s"

            info_value = ctk.CTkLabel(item_frame, text=text_value, height=18)
            info_value.pack(padx=3, pady=2)

            info_table_frame.grid_columnconfigure(index, weight=1)

        graph_row = 2
        if level.bad_mapper:
            bad_mapper_text = "On this map notes can be parsed incorrectly! NPS and graph can display incorrect info!"
            self.bad_mapper_label = ctk.CTkLabel(self.level_info_frame, text=bad_mapper_text, padx=self.padding)
            self.bad_mapper_label.grid(row=graph_row, column=0, sticky="w")
            graph_row += 1

        # Graph
        centers = (level.edges[:-1] + level.edges[1:]) / 2
        plt.plot(centers, level.counts, linewidth=2, color=self.button_colors[level.difficulty])

        ax = plt.gca()
        original_ticks = ax.get_yticks()
        normalized_ticks = original_ticks / self.settings.bin_size
        ax.set_ylabel("NPS")
        ax.set_yticks(original_ticks)
        ax.set_yticklabels([f'{tick:.2f}' for tick in normalized_ticks])
        ax.set_ylim(bottom=0)

        canvas = FigureCanvasTkAgg(plt.gcf(), master=self.level_info_frame)
        canvas.get_tk_widget().grid(row=graph_row, column=0, sticky="nsew", padx=self.padding, pady=self.padding)
        self.level_info_frame.grid_rowconfigure(graph_row, weight=1)
        self.level_info_frame.grid_columnconfigure(0, weight=1)
        self.after(100, canvas.draw) # Fix for figure jumping for 1 frame


if __name__ == "__main__":
    app = BSMapInfoApp()
    app.after(5, app.change_target_dir)
    app.mainloop()