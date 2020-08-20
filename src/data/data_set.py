import csv
import random

from data.data_point import DataPoint


class Dataset:
    def __init__(self, csv_file):
        with open(csv_file, mode='r') as f:
            csv_reader = csv.DictReader(f)
            self.data_points = [DataPoint(entry['path'], int(entry['reference_value'])) for entry in csv_reader]

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
