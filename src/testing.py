import numpy as np
from evaluation.evaluation import per_slide_evaluation
from data.data_set import Dataset
from evaluation.roc import evaluate_by_roc_curve
import matplotlib.pyplot as plt
from tensorflow.keras.models import load_model
from model.inceptionv3_model import InceptionModel

if __name__ == '__main__':
    #test_dataset = Dataset('/home/dschacherer/Schreibtisch/testdata_out/csv_test_norm_cancer.csv', num_classes=3)
    #res=per_slide_evaluation('dummy', test_dataset)
    #print(res)
    #fig = plt.figure()
    #evaluate_by_roc_curve(fig, res)
    #plt.show()

    #import json
    #import matplotlib.pyplot as plt
    #with open('/home/dschacherer/Schreibtisch/training_history.json', 'r') as json_file: 
    #    history = json.load(json_file)
    #    plt.plot(history['loss'], label='training loss')
    #    plt.plot(history['val_loss'], label='validation loss')
    #    plt.title('Training and validation loss')
    #    plt.xlabel('epoch')
    #    plt.ylabel('cross entropy loss')
    #    plt.legend(loc='upper right')
    #    plt.savefig('/home/dschacherer/Schreibtisch/loss.png')
    print('hello')
    model = load_model('/mnt/gaia/imageData/deep_learning/output/imaging-data-commons/idc-pathomics-use-case-1/trained_model', compile=True)
    print(model)