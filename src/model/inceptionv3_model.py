import tensorflow as tf 
from tensorflow.keras.layers import GlobalAveragePooling2D, Dense
from tensorflow.keras import Model
from tensorflow.keras.models import load_model

from model.base_model import BaseModel

class InceptionModel(BaseModel):

    def _create_model(self, num_classes=2, load_trained_model_from=None):
        # Load already trained model if the path is given
        if load_trained_model_from: 
            model = load_model(load_trained_model_from, compile=False)
            return model 

        # Binary classification problem: we use single output value obtained from a sigmoid layer instead of two output values from a softmax layer
        if num_classes == 2: 
            num_classes = 1  
            classifier_activation = 'sigmoid'
            loss = 'binary_crossentropy'
        if num_classes > 2: 
            classifier_activation = 'softmax'
            loss = 'categorical_crossentropy'

        # Use Inception v3 model by Keras and add top layers manually 
        model = tf.keras.applications.InceptionV3(include_top=False, weights=None, input_shape=(512, 512, 3))
        model = self._add_top_layers(model, classifier_activation, num_classes)
        opt = tf.keras.optimizers.RMSprop(lr=0.1, rho=0.9, momentum=0.9, epsilon=1e-6) # ensure that rho = weight decay!
        model.compile(optimizer=opt, loss=loss)
        return model

    def _add_top_layers(self, model, classifier_activation, num_classes):
        output = model.layers[-1].output
        output = GlobalAveragePooling2D()(output)
        output = Dense(num_classes, activation=classifier_activation, name='predictions')(output)
        return Model(model.input, output)

