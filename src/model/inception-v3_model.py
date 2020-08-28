import tensorflow as tf 


from base_model import BaseModel

class InceptionModel(BaseModel):

    def _create_model(self, num_classes=2):
        # Binary classification problem: we use single output value obtained from a sigmoid layer instead of two output values from a softmax layer
        if num_classes == 2: 
            num_classes = 1  
            classifier_activation = 'sigmoid'
            loss = 'binary_crossentropy'
        if num_classes > 2: 
            classifier_activation = 'softmax'
            loss = 'categorical_crossentropy'

        model = tf.keras.applications.InceptionV3(include_top=True, weights=None, classes=num_classes, classifier_activation=classifier_activation)
        opt = tf.keras.optimizers.RMSprop(lr=0.1, rho=0.9, momentum=0.9, epsilon=1e-6) # ensure that rho = weight decay!
        model.compile(optimizer=opt, loss=loss)
        return model 

if __name__=='__main__': 
    m=InceptionModel(num_classes=2)
    print(repr(m))
