import tkinter as tk
from Config import Settings
from TkinterClasses import MenuBar, ConfigurableFrame, LabelEntryPair
from datetime import datetime
from UIPages import CreateDatasetPage, AddDataPage, AddAnnotationsPage

settings = Settings(Settings.COMPHOME / "RNAScopeCountAppFolder", "default")
print(settings.profile)
settings.profile["button_color"] = "Gray"

main = tk.Tk()
main.geometry("{0}x{1}".format(settings.profile["window_width"], settings.profile["window_height"]))

menu = MenuBar(main, MenuBar.LEFT, settings.profile["menubar_color"], "Gray", 10)
dataset_btn = menu.add_button("Dataset", settings.profile["button_color"], "White", 2)
model_btn = menu.add_button("Model", settings.profile["button_color"], "White", 2)

tool_bar_window = ConfigurableFrame(menu.empty_frame,ConfigurableFrame.TOP, "RED")
create_dataset_tools = tool_bar_window.create_page("create_dataset")
dataset_tools_menu = MenuBar(create_dataset_tools, MenuBar.TOP, "Red", "Gray", 13)
dataset_tools_menu.add_button("Create Dataset", settings.profile["button_color"], "White", 2)
dataset_tools_menu.add_button("Add Data", settings.profile["button_color"], "White", 2)
dataset_tools_menu.add_button("Add Annotations", settings.profile["button_color"], "White", 2)

create_model_tools = tool_bar_window.create_page("create_model")
model_tools_menu = MenuBar(create_model_tools, MenuBar.TOP, "Red", "Gray", 13)
model_tools_menu.add_button("Create Model", settings.profile["button_color"], "White", 2)

main_window = ConfigurableFrame(menu.empty_frame,ConfigurableFrame.TOP, "Gray")
create_dataset_page = CreateDatasetPage(main_window)
add_data_page = AddDataPage(main_window, settings.working_path)
add_annotations_page = AddAnnotationsPage(main_window, settings.working_path)

menu.add_listener("Model",lambda event: tool_bar_window.load_page("create_model"))
menu.add_listener("Dataset",lambda event: tool_bar_window.load_page("create_dataset"))
menu.add_listener("Dataset",lambda event: main_window.load_page(create_dataset_page.name))

dataset_tools_menu.add_listener("Create Dataset",lambda event: main_window.load_page(create_dataset_page.name))
dataset_tools_menu.add_listener("Add Data",lambda event: main_window.load_page(add_data_page.name))
dataset_tools_menu.add_listener("Add Data", lambda event: add_data_page.NameDropDown.update_dropdown(add_data_page.get_datasets(settings.working_path)))
dataset_tools_menu.add_listener("Add Annotations", lambda event: main_window.load_page(add_annotations_page.name))
dataset_tools_menu.add_listener("Add Annotations", lambda event: add_annotations_page.NameDropDown.update_dropdown(add_annotations_page.get_datasets(settings.working_path)))

create_dataset_page.add_listener("Create", lambda event: create_dataset_page.create_dataset(settings.working_path))
add_data_page.add_listener("Add Data", lambda event: add_data_page.add_images(settings.working_path))
add_annotations_page.add_listener("Add Annotation", lambda event: add_annotations_page.add_annotations(settings.working_path))

tk.mainloop()