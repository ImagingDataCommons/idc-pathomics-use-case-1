import os
import random
import numpy as np
import tensorflow as tf
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.models import load_model
from data.data_set import Dataset
from data.data_point import DataPoint


class BaseModel:
    def __init__(self, *args, **kwargs):
        self.model = self._create_model(*args, **kwargs)
    
    @classmethod
    def load(self, file_path: str) -> None:
        self.model = load_model(load_trained_model_from, compile=False)

    def _create_model(self, *args, **kwargs):
        raise NotImplementedError

    def __repr__(self) -> str:
        lines = []
        self.model.summary(print_fn=lambda line: lines.append(line))
        return os.linesep.join(lines)

    def train(self, training_dataset: Dataset, batch_size: int, epochs: int, output_path: str, validation_dataset: Dataset = None, max_queue_size: int = 100) -> tf.keras.callbacks.History:

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

        save_model = ModelCheckpoint(
            filepath=os.path.join(output_path, 'checkpoint_{epoch:03d}'), 
            save_weights_only=False, 
            monitor='val_loss', 
            mode='min',
            save_best_only=True
        )

        history = self.model.fit(
            training_generator,
            epochs=epochs,
            max_queue_size=max_queue_size,
            steps_per_epoch=len(training_dataset)//batch_size,
            validation_data=validation_generator,
            validation_steps=validation_steps, 
            callbacks=[save_model]
        )
        return history

    def make_prediction(self, data_point: DataPoint) -> np.ndarray:
        # add batch dimension
        patch = data_point.get_patch()[np.newaxis, ...]
        prediction = self.model(patch)
        # remove batch dimension
        return prediction[0, ...]
    
    def save(self, file_path: str) -> None:
        self.model.save(
            file_path,
            overwrite=True,
            include_optimizer=False
        )
