import os
import sys
import customtkinter as ctk
import matplotlib.pyplot as plt

from PIL import Image
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from settings_handler import SettingsHandler
from info_schema_version_handler import InfoSchemaVersionHandler
from level_schema_version_handler import LevelSchemaVersionHandler


VERSION = "1.0.1"
AUTHOR = "Khivus"
APP_NAME = "BSMapInfo"
FULL_APP_NAME = "Beat Saber Map Info"


# python -m PyInstaller --windowed --onefile --icon="icon.ico" src/BSMapInfo.py


class BSMapInfoApp(ctk.CTk):
    
    def __init__(self) -> None:
        super().__init__()

        ctk.set_appearance_mode("dark")
        self.title(FULL_APP_NAME)
        self.iconbitmap(sys.executable)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.set_state()
        self.set_geometry()
        self.build_ui()

        if self.settings.target_dir:
            self.load_map_list()


    def set_state(self):

        self.last_active_sidebar_btn_index = -1
        self.last_active_levels_btn_index = -1
        self.maps = []

        self.padding = 5
        self.active_btn_color = "#144870"
        self.default_btn_color = "#1F6AA5"

        self.search_var = ctk.StringVar(value="Search...")
        
        self.settings = SettingsHandler(APP_NAME)


    def set_geometry(self):
        size, x, y = self.settings.geometry.split('+')
        width, height = size.split('x')

        if x == "-1" or y == "-1":
            x = (self.winfo_screenwidth() - int(width)) // 2
            y = (self.winfo_screenheight() - int(height)) // 2

        self.geometry(f"{width}x{height}+{x}+{y}")
        self.minsize(850, 500)


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
        self.sidebar = ctk.CTkFrame(self.main_frame, width=200)
        self.sidebar.grid(row=0, column=0, sticky="nsew")

        # Search frame
        self.search_frame = ctk.CTkFrame(self.sidebar, width=200, height=38)
        self.search_frame.grid(row=0, column=0, sticky="nsew", pady=self.padding, padx=self.padding)

        # Maps list frame
        self.maps_list_frame = ctk.CTkScrollableFrame(self.sidebar, width=200)
        self.maps_list_frame.grid(row=1, column=0, sticky="nsew", pady=self.padding, padx=self.padding)
        self.sidebar.grid_rowconfigure(1, weight=1)

        # Graph frame
        self.graph_frame = ctk.CTkFrame(self.main_frame)
        self.graph_frame.grid(row=0,column=1, sticky="nsew")

        self.main_frame.grid_columnconfigure(1, weight=1)
        self.main_frame.grid_rowconfigure(0, weight=1)

        # Levels frame
        self.levels_frame = ctk.CTkFrame(self.graph_frame, height=38)
        self.levels_frame.grid(row=0,column=0, sticky="nsew", pady=self.padding, padx=self.padding)

        # Level info frame
        self.level_info_frame = ctk.CTkFrame(self.graph_frame)
        self.level_info_frame.grid(row=1,column=0, sticky="nsew", pady=self.padding, padx=self.padding)

        self.graph_frame.grid_columnconfigure(0, weight=1)
        self.graph_frame.grid_rowconfigure(1, weight=1)

        # Topbar items
        self.stacked_counted_btn = ctk.CTkButton(self.topbar, text="Stacked counted", width=50, command=lambda: self.toggle(self.settings.stacked_counted, self.stacked_counted_btn))
        self.stacked_counted_btn.pack(side="left", padx=5)
        self.update_toggle_button(self.settings.stacked_counted, self.stacked_counted_btn)
        self.settings.stacked_counted.trace_add("write", self.update_level_info)

        self.different_color_counted_btn = ctk.CTkButton(self.topbar, text="Different color counted", width=50, command=lambda: self.toggle(self.settings.different_color_counted, self.different_color_counted_btn))
        self.different_color_counted_btn.pack(side="left", padx=5)
        self.update_toggle_button(self.settings.different_color_counted, self.different_color_counted_btn)
        self.settings.different_color_counted.trace_add("write", self.update_level_info)

        self.bin_size_label = ctk.CTkLabel(self.topbar, text="Bin size (sec)")
        self.bin_size_label.pack(side="left", padx=5)
        self.bin_size_entry = ctk.CTkEntry(self.topbar, width=50, placeholder_text="3")
        self.bin_size_entry.insert(0, f"{self.settings.bin_size}")
        self.bin_size_entry.pack(side="left", padx=5)
        self.bin_size_entry.bind("<Key>", self.validate_only_digits)

        self.min_idle_time_label = ctk.CTkLabel(self.topbar, text="Min idle time (sec)")
        self.min_idle_time_label.pack(side="left", padx=5)
        self.min_idle_time_entry = ctk.CTkEntry(self.topbar, width=50, placeholder_text="3")
        self.min_idle_time_entry.insert(0, f"{self.settings.min_idle_time}")
        self.min_idle_time_entry.pack(side="left", padx=5)
        self.min_idle_time_entry.bind("<Key>", self.validate_only_digits)

        self.update_btn = ctk.CTkButton(self.topbar, text="Update", width=50, command=self.update_level_info)
        self.update_btn.pack(side="left", padx=5)

        self.change_dir_btn = ctk.CTkButton(self.topbar, text="Change directory", width=100, command=lambda: self.change_target_dir(True))
        self.change_dir_btn.pack(side="left", padx=5)

        self.about_btn = ctk.CTkButton(self.topbar, text="About", width=50, command=self.show_about)
        self.about_btn.pack(side="left", padx=5)

        # Search items
        self.search_entry = ctk.CTkEntry(self.search_frame , textvariable=self.search_var)
        self.search_entry.pack(pady=5, padx=5, fill="x")
        self.search_var.trace_add("write", self.filter_sidebar)


    def on_closing(self):
        self.settings.geometry = self.geometry()
        self.settings.save_settings()
        plt.close('all')
        app.quit()
        app.destroy()


    def change_target_dir(self, forced = False):
        if self.settings.target_dir and not forced:
            return
        
        selected_dir = ctk.filedialog.askdirectory(
            title="Select custom maps folder"
        )

        if not selected_dir:
            no_dir_label = ctk.CTkLabel(self.level_info_frame, text="Please select custom maps folder using \"Change directory\" button.")
            no_dir_label.pack(padx=self.padding * 2, anchor="w")
            self.update()
            return

        if selected_dir == self.settings.target_dir:
            return

        self.settings.target_dir = selected_dir

        self.clear_frame(self.maps_list_frame)
        self.clear_frame(self.levels_frame)
        self.clear_frame(self.level_info_frame)
        self.last_active_sidebar_btn_index = -1
        self.last_active_levels_btn_index = -1
        self.maps = []

        self.progress_bar_label = ctk.CTkLabel(self.level_info_frame, text="Loading maps...")
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
            self.load_level(map_index=self.last_active_sidebar_btn_index, level_index=self.last_active_levels_btn_index, forced=True)


    def show_about(self):
        self.about_window = ctk.CTkToplevel(self)
        self.about_window.geometry("190x108")
        self.about_window.resizable(False, False)
        self.about_window.title(f"About {APP_NAME}")
        
        self.about_window.transient(self)
        self.about_window.grab_set()

        self.about_window.update_idletasks()
        x = self.winfo_x() + ((self.winfo_width() - self.about_window.winfo_width()) // 2)
        y = self.winfo_y() + ((self.winfo_height() - self.about_window.winfo_height()) // 2)
        self.about_window.geometry(f"+{x}+{y}")

        label = ctk.CTkLabel(self.about_window, text=f"{FULL_APP_NAME}\nVersion {VERSION}\nBy: {AUTHOR}", justify="center")
        label.pack(expand=True, pady=self.padding)

        close_btn = ctk.CTkButton(self.about_window, text="Ok", command=self.about_window.destroy)
        close_btn.pack(pady=self.padding)


    def filter_sidebar(self, *args):
        query = self.search_var.get().lower()
        for index, item in enumerate(self.maps):
            if query in self.maps[index]["map"].song_title.lower() or query in self.maps[index]["map"].song_autor.lower() or query in self.maps[index]["map"].level_autor.lower():
                item["btn"].pack_forget()
                item["btn"].pack(pady=5, fill="x")
            else:
                item["btn"].pack_forget()
        self.maps_list_frame._parent_canvas.yview_moveto(0)


    def load_map_list(self, progress_bar_enabled = False):

        if progress_bar_enabled:
            self.progress_bar_label.pack(padx=self.padding * 2, pady=self.padding, anchor="w")
            self.progress_bar.pack(padx=self.padding * 2, fill="x")
            self.progress_bar.set(0)
            self.progress_bar.start()
            self.update()

        os.chdir(self.settings.target_dir)
        list_dir = os.listdir()
        list_dir_len = len(list_dir)
        update_ticks = int(list_dir_len / 5)

        for index, item in enumerate(list_dir):
            
            dir_path = os.path.join(os.getcwd(), item)
            if not os.path.isdir(dir_path):
                continue

            map = InfoSchemaVersionHandler(map_path=dir_path)

            map_btn_frame = ctk.CTkFrame(self.maps_list_frame, height=50, fg_color=("gray80", "gray20"))
            map_btn_frame.pack(pady=5, fill="x")
            map_btn_frame.pack_propagate(False)

            map_image_path = os.path.join(map.map_path, map.cover_image_filename)
            orig_map_image = Image.open(map_image_path)
            map_image = ctk.CTkImage(light_image=orig_map_image, size=(40, 40))

            map_image_label = ctk.CTkLabel(map_btn_frame, image=map_image, text="")
            map_image_label.grid(row=0, column=0, padx=self.padding, pady=self.padding, sticky="n")

            map_info = f"{map.song_title}\n"
            map_info += f"By: {map.song_autor}\n" if map.song_autor else ""
            map_info += f"Map by: {map.level_autor}" if map.level_autor else ""

            map_info_label = ctk.CTkLabel(map_btn_frame, text=map_info, wraplength=148, justify="left")
            map_info_label.grid(row=0, column=1, pady=self.padding, sticky="nw")

            self.bind_all_children(map_btn_frame, index)

            self.maps.append({"map" : map, "btn" : map_btn_frame})

            if progress_bar_enabled and not index % update_ticks:
                self.progress_bar.set(index / list_dir_len)
                self.update()

        if progress_bar_enabled:
            self.progress_bar.stop()
            self.progress_bar_label.pack_forget()
            self.progress_bar.pack_forget()

        start_info_label = ctk.CTkLabel(self.level_info_frame, text="Select map on the left sidebar to see info about it.")
        start_info_label.pack(padx=self.padding * 2, anchor="w")


    def bind_all_children(self, parent, index):

        parent.bind("<Button-1>", lambda event, i=index : self.load_map(i))
        parent.bind("<Enter>", lambda event, i=index : self.on_enter(i))
        parent.bind("<Leave>", lambda event, i=index : self.on_leave(i))

        for child in parent.winfo_children():
            self.bind_all_children(child, index)


    def on_enter(self, index): self.maps[index]["btn"].configure(fg_color=("gray90", "gray30"))
    def on_leave(self, index, forced = False):
        if self.last_active_sidebar_btn_index != index or forced:
            self.maps[index]["btn"].configure(fg_color=("gray80", "gray20"))


    def load_map(self, index: int):
        if self.last_active_sidebar_btn_index == index:
            return

        # Clear frames
        self.clear_frame(self.levels_frame)
        self.clear_frame(self.level_info_frame)
        
        # Clear button selector
        if self.last_active_sidebar_btn_index != -1:
            self.on_leave(self.last_active_sidebar_btn_index, True)

        # Set active color for selected button
        self.on_enter(index)

        # Clear level button index
        self.last_active_levels_btn_index = -1

        map: InfoSchemaVersionHandler = self.maps[index]["map"]

        self.map_levels = []
        i = 0

        for i, level in enumerate(map.levels):
            lvl_btn = ctk.CTkButton(
                self.levels_frame, 
                text=f"{map.characteristics[level['characteristic']]} {level['difficulty']}",
                command=lambda li=i  : self.load_level(map_index=index, level_index=li)
            )
            lvl_btn.grid(row=i // 6, column=i % 6, padx=self.padding, pady=self.padding, sticky="ew")
            self.levels_frame.grid_columnconfigure(i, weight=1)
            self.map_levels.append({"level" : level, "btn" : lvl_btn})

        self.last_active_sidebar_btn_index = index

        self.load_level(map_index=index, level_index=0)
        

    def clear_frame(self, frame: ctk.CTkFrame | ctk.CTkScrollableFrame):
        for widget in frame.winfo_children():
            widget.destroy()


    def load_level(self, map_index: int, level_index: int, forced = False):
        if self.last_active_levels_btn_index == level_index and not forced:
            return
        
        self.clear_frame(self.level_info_frame)
        plt.close('all')

        map: InfoSchemaVersionHandler = self.maps[map_index]["map"]
        level_file_path = os.path.join(map.map_path, self.map_levels[level_index]["level"]["filename"])
        level = LevelSchemaVersionHandler(
            characteristic=self.map_levels[level_index]["level"]["characteristic"],
            difficulty=self.map_levels[level_index]["level"]["difficulty"],
            njs=self.map_levels[level_index]["level"]["njs"],
            filepath=level_file_path)

        # Clear last button active
        if self.last_active_levels_btn_index != -1:
            self.map_levels[self.last_active_levels_btn_index]["btn"].configure(fg_color=self.default_btn_color)

        # Set active button color
        self.map_levels[level_index]["btn"].configure(fg_color=self.active_btn_color)

        # Set level in label
        self.map_name = ctk.CTkLabel(self.level_info_frame, text=f"{map.song_title}: {level.characteristic} {level.difficulty}")
        self.map_name.grid(row=0, column=0, padx=self.padding * 2, sticky="w")

        self.last_active_levels_btn_index = level_index

        if not level.notes_in_beats:
            error_text = "Can't find notes in map!"
            self.error_label = ctk.CTkLabel(self.level_info_frame, text=error_text)
            self.error_label.grid(row=1, column=0, padx=self.padding * 2, sticky="w")
            return
        
        # Getting level info
        level.beats_to_seconds(bpm=map.bpm)
        level.count_notes_density(bin_size=self.settings.bin_size, stacked_counted=self.settings.stacked_counted.get(), different_color_counted=self.settings.different_color_counted.get())
        level.count_short_stats(bin_size=self.settings.bin_size, min_idle_time=self.settings.min_idle_time)
        
        # Level info
        nps_text = f"NPS: avg = {level.mean_nps:.2f}, max = {level.max_nps:.2f}, min = {level.min_nps:.2f}. NJS = {level.njs:.1f}"
        self.nps_label = ctk.CTkLabel(self.level_info_frame, text=nps_text)
        self.nps_label.grid(row=1, column=0, padx=self.padding * 2, sticky="w")

        duration = self.time_adjust(map.song_duration if map.song_duration else level.notes_density[len(level.notes_density) - 1]['end'])
        idle = self.time_adjust(level.sum_idle)

        duration_text = f"Song duration: {duration}, idle time: {idle}"
        self.duration_label = ctk.CTkLabel(self.level_info_frame, text=duration_text)
        self.duration_label.grid(row=2, column=0, padx=self.padding * 2, sticky="w")       

        graph_row = 3
        if level.bad_mapper:
            bad_mapper_text = "On this map notes can be parsed incorrectly! NPS and graph can display incorrect info!"
            self.bad_mapper_label = ctk.CTkLabel(self.level_info_frame, text=bad_mapper_text, padx=self.padding)
            self.bad_mapper_label.grid(row=3, column=0, sticky="w")
            graph_row += 1

        # Graph
        centers = (level.edges[:-1] + level.edges[1:]) / 2
        plt.plot(centers, level.counts, 'b-', linewidth=2)

        ax = plt.gca()
        original_ticks = ax.get_yticks()
        normalized_ticks = original_ticks / self.settings.bin_size
        ax.set_ylabel("NPS")
        ax.set_yticks(original_ticks)
        ax.set_yticklabels([f'{tick:.2f}' for tick in normalized_ticks])
        ax.set_ylim(bottom=0)

        canvas = FigureCanvasTkAgg(plt.gcf(), master=self.level_info_frame)
        canvas.get_tk_widget().grid(row=graph_row, column=0, sticky="nwes")
        self.level_info_frame.grid_rowconfigure(graph_row, weight=1)
        self.level_info_frame.grid_columnconfigure(0, weight=1)
        self.after(100, canvas.draw) # Fix for figure jumping for 1 frame

    def time_adjust(self, timve) -> str:
        if timve >= 60:
            return f"{timve // 60} min {timve % 60} sec"
        else:
            return f"{timve} sec"


if __name__ == "__main__":
    app = BSMapInfoApp()
    app.after(5, app.change_target_dir)
    app.mainloop()