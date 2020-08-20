import numpy as np

class DataPoint:
    def __init__(self, patch_path, reference_value):
        self.patch_path = patch_path
        self.reference_value = reference_value

    def get_patch(self):
        return np.zeros((512, 512, 3))

    def get_reference_value(self):
        return self.reference_value

    def get_patient_id(self):
        return "xyz"

    def get_slide_id(self):
        return self.patch_path

    def get_position(self):
        return 0, 0