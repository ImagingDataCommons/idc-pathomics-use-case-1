#!/usr/bin/env python
# coding: utf-8

# # Training only

# In[8]:


import json
from data.data_set import Dataset
from model.inceptionv3_model import InceptionModel
#from model.dummy_model import DummyModel

dataset_train = Dataset('/home/dschacherer_fme/input/csv_train_norm_cancer.csv', num_classes=2)
dataset_valid = Dataset('/home/dschacherer_fme/input/csv_valid_norm_cancer.csv', num_classes=2)
model = InceptionModel(num_classes=2)
#model = DummyModel()
print(model)

history = model.train(dataset_train, batch_size=16, epochs=300, output_path='/home/dschacherer_fme/output', validation_dataset=dataset_valid)

# save final model and history
model.save('/home/dschacherer_fme/output/trained_model')
with open('/home/dschacherer_fme/output/training_history.json', 'w') as hist:
    json.dump(history.history, hist)

# some prediction
data_point = dataset_valid.data_points[0]
prediction = model.make_prediction(data_point)
print('prediction on some sample: %f (reference is %d)' % (prediction, data_point.get_reference_value()))


# In[ ]:




