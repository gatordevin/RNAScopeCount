from pathlib import Path
import json
import atexit

class Settings:
    COMPHOME = Path.home()
    def __init__(self, working_path, profile_name):
        self.update_working_path(working_path)
        self.working_path.mkdir(parents=True,exist_ok=True)

        self.settings_folder = self.working_path / "settings"
        self.settings_folder.mkdir(parents=True,exist_ok=True)
        self.update_profile(profile_name)
        atexit.register(lambda: self.save_profile(self.profile_name))

    def update_working_path(self, working_path):
        self.working_path = working_path

    def update_profile(self, profile_name):
        self.profile_name = profile_name
        profile_path = self.settings_folder / f"{profile_name}.json"
        if(profile_path.is_file()):
            with open(str(profile_path), "r") as profile_file:
                self.profile = json.load(profile_file)
        else:
            self.load_default_settings()
            self.save_profile(profile_name)
    
    def save_profile(self, profile_name):
        profile_path = self.settings_folder / f"{profile_name}.json"
        with open(str(profile_path), "w") as profile_file:
            json.dump(self.profile, profile_file)

    def load_default_settings(self):
        self.profile = {}
        self.profile["window_width"] = 800
        self.profile["window_height"] = 600
        self.profile["menubar_color"] = "Red"