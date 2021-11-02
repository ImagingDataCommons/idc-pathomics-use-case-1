import pandas as pd
import sys
from ast import literal_eval

if __name__=='__main__':
    data = pd.read_csv(sys.argv[1])
    output_name = sys.argv[1].split('.')[0] + '.csv'
    # Get predicted value 
    predicted_values = []
    for i, row in data.iterrows():
        prediction = row['prediction']
        prediction.replace(' ', ',')
        print(prediction)
        print(literal_eval(prediction))
        predicted_value = prediction.index(max(prediction))
        predicted_values.append(predicted_value)
        break
    data['predicted_value'] = predicted_values
    print('total', len(data), 'correct', len(data[data['reference_value'] == data['predicted_value']]))
    print(data[data['reference_value'] == data['predicted_value']])
    data.to_csv(output_name)
