import os
import customtkinter as ctk
import matplotlib.pyplot as plt

from pathlib import Path
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from info_schema_version_handler import InfoSchemaVersionHandler
from level_schema_version_handler import LevelSchemaVersionHandler


VERSION = "0.1.0"
AUTHOR = "Khivus"
APP_NAME = "BSMapInfo"
FULL_APP_NAME = "Beat Saber Map Info"
# python -m PyInstaller --onefile src/BSMapInfo.py

# # settings managment
# app_dir = Path(os.path.expanduser("~")) / "AppData" / "Local" / APP_NAME
# app_dir.mkdir(parents=True, exist_ok=True)
# settings_file = app_dir / "settings.json"


class BSMapInfoApp(ctk.CTk):
    
    def __init__(self) -> None:
        super().__init__()

        ctk.set_appearance_mode("dark")
        self.title(FULL_APP_NAME)
        self.geometry("850x500")
        self.minsize(850, 500)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.set_state()
        self.build_ui()
        self.load_map_list()


    def set_state(self):

        self.last_active_sidebar_btn_index = -1
        self.last_active_levels_btn_index = -1
        self.sidebar_items = []

        self.padding = 5
        self.active_btn_color = "#144870"
        self.default_btn_color = "#1F6AA5"
        
        self.target_dir = "D:\\Git\\BSMapInfo Test Maps"
        self.bin_size = 3
        self.min_idle_time = 3

        self.search_var = ctk.StringVar(value="Search...")
        self.stacked_counted = ctk.BooleanVar(value=True)
        self.different_color_counted = ctk.BooleanVar(value=True)


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
        self.sidebar = ctk.CTkScrollableFrame(self.main_frame, width=200)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        # self.sidebar.grid_propagate(False)

        # Graph frame
        self.graph_frame = ctk.CTkFrame(self.main_frame)
        self.graph_frame.grid(row=0,column=1, sticky="nsew")

        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Levels frame
        self.levels_frame = ctk.CTkFrame(self.graph_frame, height=28)
        self.levels_frame.grid(row=0,column=0, sticky="nsew", pady=self.padding, padx=self.padding)

        # Level info frame
        self.level_info_frame = ctk.CTkFrame(self.graph_frame)
        self.level_info_frame.grid(row=1,column=0, sticky="nsew", pady=self.padding, padx=self.padding)

        self.graph_frame.grid_columnconfigure(0, weight=1)
        self.graph_frame.grid_rowconfigure(1, weight=1)

        # Topbar items
        self.stacked_counted_btn = ctk.CTkButton(self.topbar, text="Stacked counted", width=50, command=lambda: self.toggle(self.stacked_counted, self.stacked_counted_btn))
        self.stacked_counted_btn.pack(side="left", padx=5)
        self.update_toggle_button(self.stacked_counted, self.stacked_counted_btn)
        self.stacked_counted.trace_add("write", self.update_level_info)

        self.different_color_counted_btn = ctk.CTkButton(self.topbar, text="Different color counted", width=50, command=lambda: self.toggle(self.different_color_counted, self.different_color_counted_btn))
        self.different_color_counted_btn.pack(side="left", padx=5)
        self.update_toggle_button(self.different_color_counted, self.different_color_counted_btn)
        self.different_color_counted.trace_add("write", self.update_level_info)

        self.bin_size_label = ctk.CTkLabel(self.topbar, text="Bin size (sec)")
        self.bin_size_label.pack(side="left", padx=5)
        self.bin_size_entry = ctk.CTkEntry(self.topbar, width=50, placeholder_text=f"{self.bin_size}")
        self.bin_size_entry.pack(side="left", padx=5)
        self.bin_size_entry.bind("<Key>", self.validate_only_digits)

        self.min_idle_time_label = ctk.CTkLabel(self.topbar, text="Min idle time (sec)")
        self.min_idle_time_label.pack(side="left", padx=5)
        self.min_idle_time_entry = ctk.CTkEntry(self.topbar, width=50, placeholder_text=f"{self.min_idle_time}")
        self.min_idle_time_entry.pack(side="left", padx=5)
        self.min_idle_time_entry.bind("<Key>", self.validate_only_digits)

        self.update_btn = ctk.CTkButton(self.topbar, text="Update", width=50, command=self.update_level_info)
        self.update_btn.pack(side="left", padx=5)

        self.about_btn = ctk.CTkButton(self.topbar, text="About", width=50, command=self.show_about)
        self.about_btn.pack(side="right", padx=5)

        # Sidebar items
        self.search_entry = ctk.CTkEntry(self.sidebar , textvariable=self.search_var)
        self.search_entry.pack(pady=5, padx=5, fill="x")
        self.search_var.trace_add("write", self.filter_sidebar)


    def on_closing(self):
        plt.close('all')
        app.quit()
        app.destroy()


    def validate_only_digits(self, event):
        entry = event.widget
        old_value = entry.get()
        new_value = old_value + event.char

        if new_value == "" or new_value.isdigit():
            return

        if event.keysym == "BackSpace" or event.keysym == "Delete":
            return

        return "break"


    def toggle(self, var: ctk.BooleanVar, btn: ctk.CTkButton):
        var.set(False if var.get() else True)
        self.update_toggle_button(var, btn)


    def update_toggle_button(self, var: ctk.BooleanVar, btn: ctk.CTkButton):
        if var.get():
            btn.configure(fg_color=self.active_btn_color)
        else:
            btn.configure(fg_color=self.default_btn_color)


    def update_level_info(self, *args):

        try:
            bin_size = int(self.bin_size_entry.get())
        except:
            bin_size = self.bin_size

        try:
            min_idle_time = int(self.min_idle_time_entry.get())
        except:
            min_idle_time = self.min_idle_time

        if bin_size < 1 or min_idle_time < 1:
            return
        
        self.bin_size = bin_size
        self.min_idle_time = min_idle_time
        
        if self.last_active_sidebar_btn_index != -1 and self.last_active_levels_btn_index != -1:
            self.load_level(map_index=self.last_active_sidebar_btn_index, level_index=self.last_active_levels_btn_index)


    def show_about(self):
        pass


    def filter_sidebar(self, *args):
        # pass
        query = self.search_var.get().lower()
        for item in self.sidebar_items:
            if query in item["btn"].cget("text").lower():
                item["btn"].pack_forget()
                item["btn"].pack(pady=5, fill="x")
            else:
                item["btn"].pack_forget()


    def load_map_list(self):

        os.chdir(self.target_dir)

        for index, item in enumerate(os.listdir()):
            
            dir_path = os.path.join(os.getcwd(), item)
            if not os.path.isdir(dir_path):
                continue

            map = InfoSchemaVersionHandler(map_path=dir_path)

            btn = ctk.CTkButton(
                self.sidebar,
                text=f"{map.song_title}",
                command=lambda i=index : self.load_map(i)
            )

            btn.pack(pady=5, fill="x")
            self.sidebar_items.append({"map" : map, "btn" : btn})


    def load_map(self, index: int):
        # Clear frames
        self.clear_frame(self.levels_frame)
        self.clear_frame(self.level_info_frame)
        
        # Clear button selector
        if self.last_active_sidebar_btn_index != -1:
            self.sidebar_items[self.last_active_sidebar_btn_index]["btn"].configure(fg_color=self.default_btn_color)

        # Clear level button index
        self.last_active_levels_btn_index = -1

        # Set active color for selected button
        self.sidebar_items[index]["btn"].configure(fg_color=self.active_btn_color)

        map: InfoSchemaVersionHandler = self.sidebar_items[index]["map"]
        self.map_name = ctk.CTkLabel(self.level_info_frame, text=map.song_title)
        self.map_name.grid(row=0, column=0, sticky="w", padx=self.padding)

        self.map_levels = []
        for i, level in enumerate(map.levels):
            lvl_btn = ctk.CTkButton(
                self.levels_frame, 
                text=f"{level['characteristic'][0]} {level['difficulty']}",
                command=lambda li=i  : self.load_level(map_index=index, level_index=li),
                width=60
            )
            lvl_btn.grid(row=i // 8, column=i % 8, padx=self.padding, pady=self.padding, sticky="ew")
            self.levels_frame.grid_columnconfigure(i, weight=1)
            self.map_levels.append({"level" : level, "btn" : lvl_btn})

        self.last_active_sidebar_btn_index = index

        if len(self.map_levels) == 1:
            self.load_level(map_index=index, level_index=0)
        

    def clear_frame(self, frame: ctk.CTkFrame):
        for widget in frame.winfo_children():
            widget.destroy()


    def load_level(self, map_index: int, level_index: int):
        
        self.clear_frame(self.level_info_frame)
        plt.close('all')

        map: InfoSchemaVersionHandler = self.sidebar_items[map_index]["map"]
        level_file_path = os.path.join(map.map_path, self.map_levels[level_index]["level"]["filename"])
        level = LevelSchemaVersionHandler(
            characteristic=self.map_levels[level_index]["level"]["characteristic"],
            difficulty=self.map_levels[level_index]["level"]["difficulty"],
            filepath=level_file_path)

        # Clear last button active
        if self.last_active_levels_btn_index != -1:
            self.map_levels[self.last_active_levels_btn_index]["btn"].configure(fg_color=self.default_btn_color)

        # Set active button color
        self.map_levels[level_index]["btn"].configure(fg_color=self.active_btn_color)

        # Set level in label
        self.map_name = ctk.CTkLabel(self.level_info_frame, text=f"{map.song_title}: {level.characteristic} {level.difficulty}")
        self.map_name.grid(row=0, column=0, sticky="w", padx=self.padding)

        self.last_active_levels_btn_index = level_index

        if not level.notes_in_beats:
            print(f"\nCan't find notes in map {map.song_title} ({level.characteristic} {level.difficulty})!")
            return
        
        level.beats_to_seconds(bpm=map.bpm)
        level.count_notes_density(bin_size=self.bin_size, stacked_counted=self.stacked_counted.get(), different_color_counted=self.different_color_counted.get())
        level.count_short_stats(bin_size=self.bin_size, min_idle_time=self.min_idle_time)
        
        # UI thing
        nps_text = f"NPS: max = {level.max_nps:.2f}, min = {level.min_nps:.2f}, mean = {level.mean_nps:.2f}"
        self.nps_label = ctk.CTkLabel(self.level_info_frame, text=nps_text, padx=self.padding)
        self.nps_label.grid(row=1, column=0, sticky="w")

        duration_text = f"Song duration: {map.song_duration if map.song_duration else level.notes_density[len(level.notes_density) - 1]['end']} sec, idle time: {level.sum_idle} sec"
        self.duration_label = ctk.CTkLabel(self.level_info_frame, text=duration_text, padx=self.padding)
        self.duration_label.grid(row=2, column=0, sticky="w")       

        # Graph
        centers = (level.edges[:-1] + level.edges[1:]) / 2
        plt.plot(centers, level.counts, 'b-', linewidth=2)

        ax = plt.gca()
        original_ticks = ax.get_yticks()
        normalized_ticks = original_ticks / self.bin_size
        ax.set_yticks(original_ticks)
        ax.set_yticklabels([f'{tick:.2f}' for tick in normalized_ticks])
        ax.set_ylim(bottom=0)

        canvas = FigureCanvasTkAgg(plt.gcf(), master=self.level_info_frame)
        canvas.draw()
        canvas.get_tk_widget().grid(row=3, column=0, sticky="nwes")
        self.level_info_frame.grid_rowconfigure(3, weight=1)
        self.level_info_frame.grid_columnconfigure(0, weight=1)


if __name__ == "__main__":
    app = BSMapInfoApp()
    app.mainloop()