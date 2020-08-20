import random
from data.data_point import DataPoint

class Dataset:
    def __init__(self):
        self.data_points = self._init_data_points()

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

    # TODO implement
    def _init_data_points(self):
        return [DataPoint('%d_slide' % random.randint(0,5), random.randint(0,1)) for _ in range(100)]