from pandas import DataFrame

def per_slide_evaluation(model, data_set):
    slide_results = {}
    for data_point in data_set.data_points:
        slide_id = data_point.get_slide_id()
        if slide_id not in slide_results:
            slide_results[slide_id] = {
                'num_patches': 0,
                'sum_probability': 0.0,
                'num_positive': 0,
                'reference_value': data_point.get_reference_value()
            }
        
        prediction = model.predict(data_point)
        slide_results[slide_id]['num_patches'] += 1
        slide_results[slide_id]['num_positive'] += prediction > 0.5
        slide_results[slide_id]['sum_probability'] += prediction

    for slide_id in slide_results:
        slide_results[slide_id]['percentage_positive'] = slide_results[slide_id]['num_positive'] / slide_results[slide_id]['num_patches']
        slide_results[slide_id]['average_probability'] = slide_results[slide_id]['sum_probability'] / slide_results[slide_id]['num_patches']

    # turn results into pandas data frame
    result_data = {
        'slide_id': [],
        'reference_value': [],
        'percentage_positive': [],
        'average_probability': []
    }
    
    for slide_id, slide_result in slide_results.items():
        result_data['slide_id'].append(slide_id)
        result_data['reference_value'].append(slide_result['reference_value'])
        result_data['percentage_positive'].append(slide_result['percentage_positive'])
        result_data['average_probability'].append(slide_result['average_probability'])

    result_df = DataFrame(result_data)

    return result_df