import csv
import os
import random
import numpy as np
import matplotlib.pyplot as plt
from tensorflow.keras.utils import to_categorical

from data.data_point import DataPoint


class Dataset:
    
    def __init__(self, csv_file, num_classes):
        self.data_points = []
        base_path = os.path.abspath(os.path.split(csv_file)[0])
        with open(csv_file, mode='r') as f:
            csv_reader = csv.DictReader(f)
            for entry in csv_reader:
                self.data_points.append(DataPoint(
                    os.path.join(base_path, entry['path']),
                    int(entry['reference_value'])
                ))
        self.patch_width, self.patch_height, self.num_channels = self.data_points[0].get_patch().shape
        self.num_classes = num_classes

    def __len__(self):
        return len(self.data_points)

    def get_generator(self, batch_size=1, infinite=False, shuffle=False):
        indices = list(range(len(self.data_points)))
        while True:
            if shuffle:
                random.shuffle(indices)

            for batch_indices in [indices[i*batch_size : (i+1)*batch_size] for i in range(len(indices)//batch_size)]:

                batch_x = np.empty((batch_size, self.patch_width, self.patch_height, self.num_channels))
                batch_y = np.empty((batch_size))
                
                for batch_index, data_index in enumerate(batch_indices):
                    data_point = self.data_points[data_index]
                    batch_x[batch_index] = data_point.get_patch()
                    if self.num_classes == 2: 
                        batch_y[batch_index] = data_point.get_reference_value()
                    else: 
                        # if nr_classes > 2, generate one-hot-encoding for the reference 
                        batch_y[batch_index] = to_categorical(data_point.get_reference_value(), num_classes=self.num_classes) 
                
                yield batch_x, batch_y, [None]
            
            if not infinite:
                break
