import pandas as pd

class Predictions():
    
    def __init__(self, model=None, dataset=None, load_from=None):
        
        else: 
            predictions_dict = {}
            for i, data_point in enumerate(dataset.data_points):
                slide_id = data_point.get_slide_id()
                if slide_id not in predictions_dict:
                    predictions_dict[i] = {
                        'slide_id': slide_id,
                        'tile_position': data_point.get_position(),
                        'reference_value': data_point.get_reference_value(),
                        'prediction': model.make_prediction(data_point).numpy()
                    }

            self.predictions = pd.DataFrame.from_dict(predictions_dict, orient='index')
    
    @classmethod
    def load(self, file_path): 
        self.predictions = pd.read_json(file_path)

    def save(self, path):
        self.predictions.to_json(path) # remember this can be a bottleneck at some point

    def get_predictions_for_slide(self, slide_id):
        return self.predictions.loc[self.predictions['slide_id'] == slide_id]['prediction'].tolist()
    
    def get_tile_positions_for_slide(self, slide_id):
        return self.predictions.loc[self.predictions['slide_id'] == slide_id]['tile_position'].tolist()

    def get_reference_value_for_slide(self, slide_id):
        return self.predictions.loc[self.predictions['slide_id'] == slide_id]['reference_value'].tolist()[0]


    
