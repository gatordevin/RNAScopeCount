import tkinter as tk
from pathlib import Path
from tkinter import filedialog

class MenuBar:
    TOP = tk.TOP
    BOTTOM = tk.BOTTOM
    RIGHT = tk.RIGHT
    LEFT = tk.LEFT
    def __init__(self, master, side, bg_color, main_color, thickness):
        self.frame_bar = tk.Frame(master=master, bg=bg_color)
        self.empty_frame = tk.Frame(master=master, bg=main_color)
        self.side = side
        self.thickness = thickness
        if self.side in [self.TOP, self.BOTTOM]:
            self.frame_bar.pack(side=self.side, fill=tk.X)
        else:
            self.frame_bar.pack(side=self.side, fill=tk.Y)

        self.empty_frame.pack(side=self.side, fill=tk.BOTH, expand=True)
        self.button_dict = {}

    def add_button(self, text, color, text_color, size):
        self.button_dict[text] = tk.Button(master=self.frame_bar, text=text, bg=color, fg=text_color, width=self.thickness, height=size)
        if self.side in [self.TOP, self.BOTTOM]:
            self.button_dict[text].pack(side=self.LEFT)
        else:
            self.button_dict[text].pack(side=self.TOP)
        return self.button_dict[text]

    def add_listener(self, button_name, listener):
        self.button_dict[button_name].bind("<Button-1>", listener, add="+")
        
class ConfigurableFrame:
    TOP = tk.TOP
    BOTTOM = tk.BOTTOM
    RIGHT = tk.RIGHT
    LEFT = tk.LEFT
    def __init__(self, master, side, bg_color):
        self.bg_color = bg_color
        self.master = master
        self.page_frames = {}
        self.active_page = None
        self.parent_frame = tk.Frame(master=self.master)
        self.parent_frame.pack(side=tk.TOP, fill=tk.BOTH)

    def create_page(self, frame_name):
        self.page_frames[frame_name] = tk.Frame(master=self.parent_frame,bg=self.bg_color)
        return self.page_frames[frame_name]

    def load_page(self, page_name):
        for widget in self.parent_frame.winfo_children():
            widget.pack_forget()
        self.active_page = page_name
        self.page_frames[page_name].pack(side=tk.TOP, fill=tk.BOTH)
    
class LabelEntryPair:
    Text = "0"
    Directory = "1"
    MultiFile = "2"
    SingleFile = "3"
    def __init__(self, master, label_name, entry_mode, config=None, default=None, allowed_file_types=[]):
        self.allowed_file_types = allowed_file_types
        self.default = default
        self.config = config
        self.entry_mode = entry_mode
        frame = tk.Frame(master=master, height=30)
        
        label = tk.Label(master=frame, width=15, text=label_name, bg="black", fg="white", relief=tk.FLAT)
        label.pack(side=tk.LEFT)
        self.var = tk.StringVar()
        if(default is not None):
            if(self.config != None):
                self.var.set(self.config.config[self.default])
            else:
                self.var.set(self.default)
        else:
            self.var.set("")
        self.entry = tk.Entry(master=frame, textvariable=self.var)
        self.entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.var.trace("w", lambda name, index, mode, var=self.var: self.textbox_change(var))

        if(entry_mode==self.Text):
            pass
        elif(entry_mode==self.Directory):
            button = tk.Button(master=frame, width=5, text="...", bg="black", fg="white", relief=tk.FLAT)
            button.pack(side=tk.RIGHT)
            button.bind("<Button-1>", self.select_directory)
        elif(entry_mode==self.MultiFile):
            button = tk.Button(master=frame, width=5, text="...", bg="black", fg="white", relief=tk.FLAT)
            button.pack(side=tk.RIGHT)

            button.bind("<Button-1>", self.select_multifile)
        elif(entry_mode==self.SingleFile):
            button = tk.Button(master=frame, width=5, text="...", bg="black", fg="white", relief=tk.FLAT)
            button.pack(side=tk.RIGHT)

            button.bind("<Button-1>", self.select_file)
        
        frame.pack(fill=tk.X, side=tk.TOP)

    def error(self):
        self.entry.configure(bg="Red")

    def select_directory(self, event):
        path = Path(filedialog.askdirectory(initialdir = self.var.get()))
        self.var.set(path)
        if(self.config!= None):
            self.config.config[self.default] = self.var.get()

    def select_multifile(self, event):
        filepaths = filedialog.askopenfilenames(filetypes=self.allowed_file_types)
        super_string = ""
        for filepath in filepaths:
            super_string += str(Path(filepath))+","
        self.var.set(super_string)
        if(self.config!= None):
            self.config.config[self.default] = self.var.get()

    def select_file(self, event):
        path = Path(filedialog.askopenfilename())
        self.var.set(path)
        if(self.config!= None):
            self.config.config[self.default] = self.var.get()

    def textbox_change(self, var):
        self.entry.configure(bg="White")
        if(self.config!= None):
            self.config.config[self.default] = self.var.get()

class LabelDropDownPair:
    def __init__(self, container_frame, label_name, dropdown_list, config=None, default=None):
        self.default = default
        self.config = config
        self.dropdown_list = dropdown_list
        self.dropdown_list.insert(0,"")
        self.frame = tk.Frame(master=container_frame, height=30)
        
        label = tk.Label(master=self.frame, width=15, text=label_name, bg="black", fg="white", relief=tk.FLAT)
        label.pack(side=tk.LEFT)
        
        self.var = tk.StringVar()
        if(default is not None):
            self.var.set(config.config[default])
        else:
            self.var.set(dropdown_list[0])

        self.optmnu_data_type = tk.OptionMenu(self.frame, self.var, *dropdown_list, command=self.drop_down_changed)
        self.optmnu_data_type.pack(side=tk.LEFT)
        self.frame.pack(fill=tk.X, side=tk.TOP)

    def drop_down_changed(self, event):
        if(self.config is not None):
            self.config.config[self.default] = self.var.get()
        
    def update_dropdown(self, labels):
        for label in labels:
            if label not in self.dropdown_list:
                self.optmnu_data_type["menu"].add_command(label=label, command=lambda value=label: self.var.set(value))

class CheckButtonAndHide:
    def __init__(self, container_frame, label_name, frame_to_toggle):
        frame = tk.Frame(master=container_frame, height=30)
        self.frame_to_toggle = frame_to_toggle
        label = tk.Label(master=frame, width=15, text=label_name, bg="black", fg="white", relief=tk.FLAT)
        label.pack(side=tk.LEFT)
        
        self.menu_hide = tk.IntVar()
        self.menu_hide.set(0)
        ckbtn_import = tk.Checkbutton(frame, variable=self.menu_hide)
        ckbtn_import.pack(side=tk.LEFT)
        ckbtn_import.bind("<Button-1>", self.import_annotations)
        frame.pack(fill=tk.X, side=tk.TOP)

    def import_annotations(self, event):
        if(self.menu_hide.get() == 1):
            self.frame_to_toggle.pack_forget()
        else:
            self.frame_to_toggle.pack()