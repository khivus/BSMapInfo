import os
import customtkinter as ctk

from info_schema_version_handler import InfoSchemaVersionHandler


class App(ctk.CTk):
    
    def __init__(self) -> None:
        super().__init__()

        ctk.set_appearance_mode("dark")
        self.title("Beat Saber Map Info")
        self.geometry("800x450")
        self.last_active_index = -1

        self.build_ui()
        self.load_map_list()


    def build_ui(self):

        # Frames
        # Topbar frame
        self.topbar = ctk.CTkFrame(self, height=40)
        self.topbar.grid(row=0, column=0, columnspan=2, sticky="nsew")

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

        # Topbar items
        self.temp_btn = ctk.CTkButton(self.topbar, text="test", width=50, command=self.temp_btn_handler)
        self.temp_btn.pack(side="left", padx=5, pady=5)

        # Sidebar items
        self.search_var = ctk.StringVar()
        self.search_entry = ctk.CTkEntry(self.sidebar, placeholder_text="Search...", placeholder_text_color="gray" , textvariable=self.search_var)
        self.search_entry.pack(pady=5, padx=5, fill="x")
        self.search_var.trace_add("write", self.filter_sidebar)

        self.sidebar_items = []

        # Graph items
        # self.graph_btn = ctk.CTkButton(self.graph_frame, text="anime", width=50, command=self.graph_btn_handler)
        # self.graph_btn.pack(padx=5, pady=5)
        # self.btn_is_visible = True


    def temp_btn_handler(self):
        pass
        # self.graph_btn.forget()
        # self.graph_btn.pack(padx=5, pady=5)

        # if not self.btn_is_visible:
        #     self.graph_btn.pack(padx=5, pady=5)
        #     self.btn_is_visible = True
        # else:
        #     # self.graph_btn.pack_forget()
        #     self.graph_btn.forget()
        #     self.btn_is_visible = False


    def filter_sidebar(self, *args):
        pass
        # query = self.search_var.get().lower()
        # for btn in self.sidebar_items:
        #     if query in btn.cget("text").lower():
        #         btn.pack_forget()
        #         btn.pack(pady=5, fill="x", before=self.sidebar_items[0])
        #     else:
        #         btn.pack_forget()


    def graph_btn_handler(self):
        pass
        # btn = ctk.CTkButton(
        #     self.sidebar,
        #     text=f"Item {len(self.sidebar_items)+1}"
        # )

        # if self.sidebar_items:
        #     btn.pack(pady=5, fill="x", before=self.sidebar_items[0])
        # else:
        #     btn.pack(pady=5, fill="x")

        # self.sidebar_items.insert(0, btn)

    
    def load_map_list(self):

        target_dir = "D:\\Git\\BSMapInfo Test Maps"
        os.chdir(target_dir)

        for index, item in enumerate(os.listdir()):
            
            item_path = os.path.join(os.getcwd(), item)
            if not os.path.isdir(item_path):
                continue

            info_file_path = os.path.join(item_path, "Info.dat")
            map = InfoSchemaVersionHandler(filepath=info_file_path)

            btn = ctk.CTkButton(
                self.sidebar,
                text=f"{map.song_title}",
                command=lambda i=index : self.load_map(i)
            )

            btn.pack(pady=5, fill="x")
            self.sidebar_items.append({"map" : map, "btn" : btn})

            # if self.sidebar_items:
            #     btn.pack(pady=5, fill="x", before=self.sidebar_items[0])
            # else:
            #     btn.pack(pady=5, fill="x")

            # self.sidebar_items.insert(0, {map : btn})


    def load_map(self, index: int):
        self.clear_frame(self.graph_frame)

        if self.last_active_index != -1:
            self.sidebar_items[self.last_active_index]["btn"].configure(fg_color="#1F6AA5")
        
        self.sidebar_items[index]["btn"].configure(fg_color="#144870")
        map = self.sidebar_items[index]["map"]

        self.map_name = ctk.CTkLabel(self.graph_frame, text=map.song_title)
        self.map_name.grid(row=0, column=0)

        self.map_bpm = ctk.CTkLabel(self.graph_frame, text=f"{map.bpm}")
        self.map_bpm.grid(row=1, column=0)

        self.map_levels = []
        for i, level in enumerate(map.levels):
            lvl = ctk.CTkLabel(self.graph_frame, text=f"{level['characteristic']} {level['difficulty']}")
            lvl.grid(row=i+2, column=0)

            self.map_levels.append(lvl)

        self.last_active_index = index
        

    def clear_frame(self, frame: ctk.CTkFrame):
        for widget in frame.winfo_children():
            widget.destroy()