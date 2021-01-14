import pandas as pd
import tensorflow as tf

from data.data_set import Dataset


class Predictions():
    
    def __init__(self, model: tf.keras.Model = None, dataset: Dataset = None, predictions: pd.DataFrame = None) -> None:

        if predictions is not None: 
            self.predictions = predictions
        else: 
            predictions_dict = {}
            for i, data_point in enumerate(dataset.data_points[:2000]):
                print(i)
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
    def load(cls, file_path: str) -> None: 
        predictions = pd.read_json(file_path)
        return cls(predictions = predictions)

    def save(self, path: str) -> None:
        self.predictions.to_json(path) # remember this can be a bottleneck at some point

    def get_predictions_for_slide(self, slide_id: str) -> list:
        return self.predictions.loc[self.predictions['slide_id'] == slide_id]['prediction'].tolist()
    
    def get_tile_positions_for_slide(self, slide_id: str) -> list:
        return self.predictions.loc[self.predictions['slide_id'] == slide_id]['tile_position'].tolist()

    def get_reference_value_for_slide(self, slide_id: str) -> int:
        return self.predictions.loc[self.predictions['slide_id'] == slide_id]['reference_value'].tolist()[0]


    
