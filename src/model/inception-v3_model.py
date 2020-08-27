import tensorflow as tf 


from base_model import BaseModel

class Model(BaseModel):

    def _create_model(self):
        model = tf.keras.applications.InceptionV3(include_top=True, weights=None, classes=1, classifier_activation='sigmoid')
        opt = tf.keras.optimizers.RMSprop(lr=0.1, rho=0.9, momentum=0.9, epsilon=1e-6) # check whether rho = weight decay!
        model.compile(optimizer=opt, loss='binary_crossentropy')
        return model

if __name__ == '__main__': 
    m = Model() 
    print(repr(m))    
