import os
import random
import numpy as np
import tensorflow as tf
from tensorflow.keras.callbacks import ModelCheckpoint


class BaseModel:
    def __init__(self, *args, **kwargs):
        self.model = self._create_model(*args, **kwargs)

    def _create_model(self, *args, **kwargs):
        raise NotImplementedError

    def __repr__(self):
        lines = []
        self.model.summary(print_fn=lambda line: lines.append(line))
        return os.linesep.join(lines)


    def train(self, training_dataset, batch_size, epochs, output_path, validation_dataset=None):

        training_generator = training_dataset.get_generator(
            batch_size=batch_size,
            infinite=True,
            shuffle=True)

        if validation_dataset:
            validation_generator = validation_dataset.get_generator(
                batch_size=1,
                infinite=True
            )
            validation_steps = len(validation_dataset)
        else:
            validation_generator = None
            validation_steps = None

        callback = ModelCheckpoint(
            filepath=os.path.join(output_path, 'checkpoint_{epoch:03d}'), 
            save_weights_only=False, 
            monitor='val_loss', 
            mode='min',
            save_best_only=True
        )
        print(callback)

        history = self.model.fit(
            training_generator,
            epochs=epochs,
            max_queue_size=100,
            steps_per_epoch=len(training_dataset)//batch_size,
            validation_data=validation_generator,
            validation_steps=validation_steps, 
            callbacks=[callback]
        )
        return history

    def make_prediction(self, data_point):
        # add batch dimension
        patch = data_point.get_patch()[np.newaxis, ...]
        prediction = self.model(patch)
        # remove batch dimension
        return prediction[0, ...]

    def save(self, file_path):
        self.model.save(
            file_path,
            overwrite=True,
            include_optimizer=False
        )
