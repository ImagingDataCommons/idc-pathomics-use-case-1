import csv
import os
import random

from data.data_point import DataPoint


class Dataset:
    def __init__(self, csv_file):
        self.data_points = []
        base_path = os.path.abspath(os.path.split(csv_file)[0])
        with open(csv_file, mode='r') as f:
            csv_reader = csv.DictReader(f)
            for entry in csv_reader:
                self.data_points.append(DataPoint(
                    os.path.join(base_path, entry['path']),
                    int(entry['reference_value'])
                ))

    def __len__(self):
        return len(self.data_points)

    def get_generator(self, infinite=False, shuffle=False):
        indices = range(len(self.data_points))
        while infinite:
            if shuffle:
                random.shuffle(indices)
            for i in indices:
                data_point = self.data_points[i]
                yield data_point.get_patch(), data_point.get_reference_value()
