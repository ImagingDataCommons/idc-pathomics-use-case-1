from tensorflow.keras import Sequential
from tensorflow.keras.layers import Conv2D, Dense, Flatten, Input, MaxPool2D
from tensorflow.keras.models import load_model

from model.base_model import BaseModel


class DummyModel(BaseModel):
    def _create_model(self, shape, load_trained_model_from=None):
        if load_trained_model_from: 
            model = load_model(load_trained_model_from, compile=True)
            model.build(shape)
            return model

        model = Sequential()
        model.add(Input(shape=shape))
        model.add(Conv2D(32, (3,3), activation='relu'))
        model.add(MaxPool2D())
        model.add(Conv2D(64, (3,3), activation='relu'))
        model.add(MaxPool2D())
        model.add(Flatten())
        model.add(Dense(1, activation='sigmoid'))

        model.compile(optimizer='adam', loss='binary_crossentropy')
        
        return model