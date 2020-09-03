import numpy as np
from pandas import DataFrame

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
        prediction = [0.4, 0.3]
        print(prediction)
        slide_results[slide_id]['num_patches'] += 1
        slide_results[slide_id]['predictions'].append(prediction)

    # average predictions of tiles to obtain one prediction per slide 
    for slide_id in slide_results:
        predictions = np.array(slide_results[slide_id]['predictions'])
        average_probability = np.average(predictions, axis=0)
        
        if get_num_classes(predictions) == 2: 
            positive = np.where(predictions >= 0.5, 1, 0)
            percentage_positive = np.average(positive, axis=0)
            
        slide_results[slide_id]['average_probability'] = average_probability
        slide_results[slide_id]['percentage_positive'] = percentage_positive
    
    print(slide_results)
        #by a) averaging tile probabilities
        
        # combine predictions to sum_prob, num_pos per class per slide 
        #slide_results[slide_id]['num_positive'] += prediction > 0.5
        #slide_results[slide_id]['sum_probability'] += prediction

    #for slide_id in slide_results:
    #    slide_results[slide_id]['percentage_positive'] = slide_results[slide_id]['num_positive'] / slide_results[slide_id]['num_patches']
    #    slide_results[slide_id]['average_probability'] = slide_results[slide_id]['sum_probability'] / slide_results[slide_id]['num_patches']

    # turn results into pandas data frame
    result_data = {
         'slide_id': [],
         'reference_value': [],
         'percentage_positive': [],
         'average_probability': []
    }
    
    #for slide_id, slide_result in slide_results.items():
    #     result_data['slide_id'].append(slide_id)
    #     result_data['reference_value'].append(slide_result['reference_value'])
    #     result_data['percentage_positive'].append(slide_result['percentage_positive'])
    #     result_data['average_probability'].append(slide_result['average_probability'])

    # result_df = DataFrame(result_data)

    return slide_results

def get_num_classes(predictions):
    try: 
        num_classes = predictions.shape[1]
    except: 
        num_classes = 2
    return num_classes