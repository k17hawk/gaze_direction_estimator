import os
from typing import List
"""
this class will take input string parameter as image path and return list of image path
"""
class ImagePathFinder:
    def __init__(self, folder_path:str):
        self.folder_path = folder_path

    def find_all_image_paths(self) -> List[str]:
        image_paths = []
        if not os.path.isdir(self.folder_path):
            print(f"Error: {self.folder_path} is not a valid directory.")
            return image_paths

        for root, dirs, files in os.walk(self.folder_path):
            for file_name in files:
                if file_name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    image_path = os.path.join(root, file_name)
                    image_paths.append(image_path)

        if not image_paths:
            print("No images found in the specified folder and its subfolders.")
        return image_paths
