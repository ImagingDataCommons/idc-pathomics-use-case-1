import os
import numpy as np
from tensorflow.keras.preprocessing.image import img_to_array, load_img
from PIL.Image import Image
from typing import List

# Path structure is /some/dirs/[SVS-FILENAME-WITHOUT-EXTENSION]_files/magnification/[X]_[Y].jpeg

class DataPoint:
    def __init__(self, patch_path: str, reference_value: int) -> None:
        self.patch_path = patch_path
        self.reference_value = reference_value

    def get_patch(self) -> Image:
        img = load_img(self.patch_path, color_mode='rgb')
        return img_to_array(img) / 255.0

    def get_reference_value(self) -> int:
        return self.reference_value

    def get_slide_id(self) -> str:
        return self.patch_path.split(os.sep)[-3][:-6]
    
    def get_position(self) -> List[int]:
        filename = os.path.split(self.patch_path)[1]
        coord_string = os.path.splitext(filename)[0]
        return [int(c) for c in coord_string.split('_')]
