import numpy as np 
import pandas as pd
import tensorflow as tf
from typing import Dict

from ..data.data_set import Dataset


class Predictions():
    
    def __init__(self, model: tf.keras.Model = None, dataset: Dataset = None, batch_size: int = 2, predictions: pd.DataFrame = None) -> None:

        if predictions is not None: 
            self.predictions = predictions
        else: 
            self.predictions = self._make_predictions(model, dataset, batch_size)
                
    @classmethod
    def load(cls, file_path: str) -> None: 
        predictions = pd.read_json(file_path)
        return cls(predictions = predictions)

    def _make_predictions(self, model: tf.keras.Model, dataset: Dataset, batch_size: int = 2) -> pd.DataFrame:
        batch_predictions = np.empty((0,3), np.float32)
        for i in range(0, len(dataset.data_points), batch_size): 
            batch = dataset.data_points[i:i+batch_size]
            batch_prediction = model.make_prediction(batch).numpy()
            batch_predictions = np.append(batch_predictions, batch_prediction, axis = 0)
        predictions_dict = self._fill_predictions_dict(dataset, batch_predictions)
        return pd.DataFrame.from_dict(predictions_dict, orient='index')

    def _fill_predictions_dict(self, dataset: Dataset, batch_predictions: np.ndarray) -> Dict: 
        predictions_dict = {}
        for i, data_point in enumerate(dataset.data_points):
            slide_id = data_point.get_slide_id()
            predictions_dict[i] = {
                'slide_id': slide_id,
                'tile_position': data_point.get_position(),
                'reference_value': data_point.get_reference_value(),
                'prediction': batch_predictions[i]
        }
        return predictions_dict

    def save(self, path: str) -> None:
        self.predictions.to_json(path)

    def get_predictions_for_slide(self, slide_id: str) -> list:
        return self.predictions.loc[self.predictions['slide_id'] == slide_id]['prediction'].tolist()
    
    def get_tile_positions_for_slide(self, slide_id: str) -> list:
        return self.predictions.loc[self.predictions['slide_id'] == slide_id]['tile_position'].tolist()

    def get_reference_value_for_slide(self, slide_id: str) -> int:
        return self.predictions.loc[self.predictions['slide_id'] == slide_id]['reference_value'].tolist()[0]
    
    def get_all_reference_values_for_slide(self, slide_id: str) -> list:
        return self.predictions.loc[self.predictions['slide_id'] == slide_id]['reference_value'].tolist()


    
