import numpy as np
import pandas as pd

def per_slide_evaluation(model, data_set):
    slide_results = {}

    for data_point in data_set.data_points:
        slide_id = data_point.get_slide_id()
        if slide_id not in slide_results:
            slide_results[slide_id] = {
                'num_patches': 0,
                'reference_value': data_point.get_reference_value(),
                'predictions': []
            }
            
        #prediction = model.predict(data_point) # frage: kommt bei n=2 dann der eine Wert auch als np datentyp raus? ist das ev. egal? sollte als list oder single value rauskommen
        prediction = 0.3
        slide_results[slide_id]['num_patches'] += 1
        slide_results[slide_id]['predictions'].append(prediction)

    # average predictions of tiles to obtain one prediction per slide 
    for slide_id in slide_results:
        predictions = np.array(slide_results[slide_id]['predictions'])
        average_probability = np.average(predictions, axis=0)

        if get_num_classes(predictions) == 2: 
            positive = np.where(predictions >= 0.5, 1, 0)
            percentage_positive = np.average(positive, axis=0)
        else: 
            percentage_positive = float('NaN')
            
        slide_results[slide_id]['average_probability'] = average_probability
        slide_results[slide_id]['percentage_positive'] = percentage_positive

    # turn results into pandas data frame
    result_data = pd.DataFrame(slide_results)
    result_data = result_data.transpose().drop('predictions', axis=1).reset_index()
    result_data.rename({'index':'slide_id'}, axis='columns', inplace=True)
    result_data.reset_index(drop=True, inplace=True)

    return result_data 


def get_num_classes(predictions):
    try: 
        num_classes = predictions.shape[1]
    except: 
        num_classes = 2
    return num_classes