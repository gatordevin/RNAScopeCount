from TkinterClasses import MenuBar, ConfigurableFrame, LabelEntryPair, LabelDropDownPair
import tkinter as tk
from datetime import datetime
import json
from pathlib import Path
from shutil import copy
import imagesize
import labelme2coco
import czifile
import numpy as np
from PIL import ImageOps, Image
import os

class CreateDatasetPage:
    def __init__(self, main_window):
        self.name = "create_dataset"
        self.create_dataset_main = main_window.create_page(self.name)
        self.dataset_name_entry = LabelEntryPair(self.create_dataset_main, "Name", LabelEntryPair.Text)
        self.get_dataset_url = LabelEntryPair(self.create_dataset_main, "URL", LabelEntryPair.Text).var.get
        self.dataset_version_entry = LabelEntryPair(self.create_dataset_main, "Version", LabelEntryPair.Text, default=1.0)
        self.get_dataset_year = LabelEntryPair(self.create_dataset_main, "Year", LabelEntryPair.Text, default=str(datetime.date(datetime.now())).split("-")[0]).var.get
        self.get_dataset_contributor = LabelEntryPair(self.create_dataset_main, "Contributor", LabelEntryPair.Text).var.get
        self.get_data_created_date = LabelEntryPair(self.create_dataset_main, "Date", LabelEntryPair.Text, default=datetime.date(datetime.now())).var.get
        self.button_dict = {}
        self.add_button("Create", "Black", "White", 2)
        
    def add_button(self, text, color, text_color, size):
        self.button_dict[text] = tk.Button(master=self.create_dataset_main, text=text, bg=color, fg=text_color, height=size)
        self.button_dict[text].pack(side=tk.TOP, fill=tk.X, expand=True)
        return self.button_dict[text]

    def add_listener(self, button_name, listener):
        self.button_dict[button_name].bind("<Button-1>", listener, add="+")

    def create_dataset(self, working_path):
        coco_dataset = {}
        coco_dataset["info"] = {}
        coco_dataset["licenses"] = []
        coco_dataset["images"] = []
        coco_dataset["annotations"] = []
        coco_dataset["categories"] = []
        coco_dataset["info"]["description"] = self.dataset_name_entry.var.get()
        print(coco_dataset["info"]["description"])
        if(coco_dataset["info"]["description"] == ""):
            self.dataset_name_entry.error()
            print("No name entered")
        else:
            coco_dataset["info"]["url"] = self.get_dataset_url()
            coco_dataset["info"]["version"] = self.dataset_version_entry.var.get()
            coco_dataset["info"]["year"] = self.get_dataset_year()
            coco_dataset["info"]["contributor"] = self.get_dataset_contributor()
            coco_dataset["info"]["data_created"] = self.get_data_created_date()
            dataset_folder_path = working_path / "dataset"
            dataset_folder_path = dataset_folder_path / f'{coco_dataset["info"]["description"]}-{coco_dataset["info"]["version"]}'
            dataset_folder_path.mkdir(parents=True,exist_ok=True)
            dataset_path = dataset_folder_path / f'{coco_dataset["info"]["description"]}-{coco_dataset["info"]["version"]}.json'
            if(dataset_path.is_file()):
                self.dataset_version_entry.error()
                print("Already exists try new version")
            else:
                with open(str(dataset_path), 'w') as outfile:
                    json.dump(coco_dataset, outfile)

class AddDataPage:
    def __init__(self, main_window, working_path):
        self.name = "add_data"
        self.add_data_main = main_window.create_page(self.name)
        self.available_datasets = self.get_datasets(working_path)
        self.NameDropDown = LabelDropDownPair(self.add_data_main, "Dataset", self.available_datasets)
        self.data_entry = LabelEntryPair(self.add_data_main, "Images", LabelEntryPair.MultiFile, allowed_file_types=[("Carl Zeiss Imaging File", "*.czi"),("JPEG", "*.jpg"),("PNG", "*.png")])
        self.license_url = LabelEntryPair(self.add_data_main, "License URL", LabelEntryPair.Text)
        self.license_name = LabelEntryPair(self.add_data_main, "License Name", LabelEntryPair.Text)
        self.button_dict = {}
        self.add_button("Add Data", "Black", "White", 2)
        
    def add_button(self, text, color, text_color, size):
        self.button_dict[text] = tk.Button(master=self.add_data_main, text=text, bg=color, fg=text_color, height=size)
        self.button_dict[text].pack(side=tk.TOP, fill=tk.X, expand=True)
        return self.button_dict[text]

    def add_listener(self, button_name, listener):
        self.button_dict[button_name].bind("<Button-1>", listener, add="+")

    def get_datasets(self, working_path):
        dataset_folder_path = working_path / "dataset"
        return [path.name for path in dataset_folder_path.iterdir()]

    def add_images(self, working_path):
        dataset_dir = working_path / "dataset"
        dataset_dir = dataset_dir / self.NameDropDown.var.get()
        json_dataset_path = dataset_dir / self.NameDropDown.var.get()
        coco_dataset = None
        with open(f"{json_dataset_path}.json") as f:
            coco_dataset = json.load(f)
            existing_image_names = []
            if(len(coco_dataset["images"])!=0):
                existing_image_names = [image["file_name"] for image in coco_dataset["images"]]
            existing_license_names = []
            if(len(coco_dataset["licenses"])!=0):
                existing_license_names = [license_data["name"] for license_data in coco_dataset["licenses"]]
            image_license_id = 0
            license_dict = {}
            license_dict["name"] = self.license_name.var.get()
            if(license_dict["name"] not in existing_license_names):
                license_dict["url"] = self.license_url.var.get()
                license_dict["id"] = len(coco_dataset["licenses"])
                coco_dataset["licenses"].append(license_dict)
                image_license_id = license_dict["id"]
            else:
                print("license already exists")
                image_license_id = existing_license_names.index(license_dict["name"])
            iidx = 0
            for image in existing_image_names:
                highest_index = int(image.split("-")[1].split(".")[0])
                iidx = highest_index + 1
            for path in self.data_entry.var.get().split(","):
                if(path != ""):
                    image_path = Path(path)
                    channel_names = ["GAD", "PV", "SOM"]
                    if(image_path.suffix == ".png"):
                        if image_path.name not in existing_image_names:
                            copy(image_path, dataset_dir)
                            image_dict = {}
                            image_dict["license"] = image_license_id
                            image_dict["file_name"] = image_path.name
                            width, height = imagesize.get(image_path)
                            image_dict["height"] = height
                            image_dict["width"] = width
                            image_dict["id"] = len(coco_dataset["images"])
                            coco_dataset["images"].append(image_dict)
                        else:
                            print("image already present")
                    elif(image_path.suffix==".czi"):
                        img = czifile.imread(image_path)
                        print(f"{img.shape[2]} channels")
                        print(f"{img.shape[4]} layers")
                        print(f"{img.shape[5]}x{img.shape[6]} image size")
                        print(f"{img.shape[7]} color channels")
                        for idx, channel in enumerate(img[0][0]):
                            img_stack = channel[0]
                            z_project_img = np.sum(img_stack, axis=0)
                            z_project_img = z_project_img.squeeze(2)
                            z_project_img = Image.fromarray(np.uint8(z_project_img), mode="L")
                            z_project_img = ImageOps.autocontrast(z_project_img,cutoff=0)
                            image_idx = "{0:0=4d}".format(iidx)
                            image_name = f"{channel_names[idx]}-{image_idx}.png"
                            if image_name not in existing_image_names:
                                z_project_img.save(dataset_dir / image_name)
                                print(dataset_dir / image_name)
                                image_dict = {}
                                image_dict["license"] = image_license_id
                                image_dict["file_name"] = image_name
                                image_dict["height"] = img.shape[6]
                                image_dict["width"] = img.shape[5]
                                image_dict["id"] = len(coco_dataset["images"])
                                coco_dataset["images"].append(image_dict)
                        # shutil.move(str(path), str(data_path / "old_files"))
                        iidx += 1
                    
        with open(f"{json_dataset_path}.json", 'w') as outfile:
            json.dump(coco_dataset, outfile)

class AddAnnotationsPage:
    def __init__(self, main_window, working_path):
        self.name = "add_annotations"
        self.add_annotations_main = main_window.create_page(self.name)
        self.available_datasets = self.get_datasets(working_path)
        self.NameDropDown = LabelDropDownPair(self.add_annotations_main, "Dataset", self.available_datasets)
        self.AnnotationEntry = LabelEntryPair(self.add_annotations_main, "Annotations", LabelEntryPair.Directory)
        self.button_dict = {}
        self.add_button("Add Annotation", "Black", "White", 2)
        
    def add_button(self, text, color, text_color, size):
        self.button_dict[text] = tk.Button(master=self.add_annotations_main, text=text, bg=color, fg=text_color, height=size)
        self.button_dict[text].pack(side=tk.TOP, fill=tk.X, expand=True)
        return self.button_dict[text]

    def add_listener(self, button_name, listener):
        self.button_dict[button_name].bind("<Button-1>", listener, add="+")

    def get_datasets(self, working_path):
        dataset_folder_path = working_path / "dataset"
        return [path.name for path in dataset_folder_path.iterdir()]

    def PolygonArea(self, corners):
        n = len(corners) # of corners
        area = 0.0
        for i in range(n):
            j = (i + 1) % n
            area += corners[i][0] * corners[j][1]
            area -= corners[j][0] * corners[i][1]
        area = abs(area) / 2.0
        return area

    def add_annotations(self, working_path):
        dataset_folder_path = working_path / "dataset"
        dataset_folder_path = dataset_folder_path / self.NameDropDown.var.get()
        image_name_list = []
        annotation_name_list = []
        for path in Path(self.AnnotationEntry.var.get()).iterdir():
            if(path.suffix==".json"):
                annotation_name_list.append(path.name.split(".")[0])
            elif(path.suffix==".png"):
                image_name_list.append(path.name.split(".")[0])
        categories = []
        json_dataset_path = dataset_folder_path / self.NameDropDown.var.get()
        coco_dataset = {}
        with open(f"{json_dataset_path}.json") as f:
            coco_dataset = json.load(f)
        for annotation_name in annotation_name_list:
            if(annotation_name in image_name_list):
                annotation_path = dataset_folder_path / annotation_name
                with open(f"{annotation_path}.json") as f:
                    annotation = json.load(f)
                    for shape in annotation["shapes"]:
                        if(shape["shape_type"] == "polygon"):
                            category_id = 0
                            if(shape["label"] not in categories):
                                category_dict = {}
                                category_dict["id"] = len(categories)
                                category_id = category_dict["id"]
                                category_dict["name"] = shape["label"]
                                categories.append(shape["label"])
                                coco_dataset["categories"].append(category_dict)
                            else:
                                category_id = categories.index(shape["label"])
                            annotation_dict = {}
                            annotation_dict["segmentation"] = []
                            points = []
                            max_x = 0
                            max_y = 0
                            min_x = 100000
                            min_y = 100000
                            point_sum = 0
                            for point in shape["points"]:
                                if(point[0]>max_x):
                                    max_x = point[0]
                                if(point[1]>max_y):
                                    max_y = point[1]
                                if(point[0]<min_x):
                                    min_x = point[0]
                                if(point[1]<min_y):
                                    min_y = point[1]
                                points.append(point[0])
                                points.append(point[1])
                                point_sum+=point[0]
                                point_sum+=point[1]
                            point_sums = []
                            if(coco_dataset["annotations"] != []):
                                for annotation in coco_dataset["annotations"]:
                                    point_sums.append(annotation["point_sum"])
                                if point_sum in point_sums:
                                    print("Existing Annotations")
                                    continue
                            annotation_dict["segmentation"].append(points)
                            annotation_dict["area"] = self.PolygonArea(shape["points"])
                            annotation_dict["iscrowd"] = 0
                            for image_data in coco_dataset["images"]:
                                name = image_data["file_name"].split(".")[0]
                                if(name == annotation_name):
                                    annotation_dict["image_id"] = image_data["id"]
                            annotation_dict["bbox"] = [min_x, min_y, max_x-min_x, max_y-min_y]
                            annotation_dict["category_id"] = category_id
                            annotation_dict["id"] = len(coco_dataset["annotations"])
                            annotation_dict["point_sum"] = point_sum
                            coco_dataset["annotations"].append(annotation_dict)
                            
        with open(f"{json_dataset_path}.json", 'w') as outfile:
            json.dump(coco_dataset, outfile)


                                

