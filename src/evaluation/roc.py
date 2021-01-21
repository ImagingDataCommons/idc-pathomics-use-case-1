import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize
from scipy import interp
from typing import Tuple, List, Dict

from evaluation.predictions import Predictions 


class ROCAnalysis():

    def __init__(self, predictions: Predictions, num_classes: int) -> None:
        self.num_classes = num_classes
        self.roc_data = self._prepare_data_for_roc_analysis(predictions)
        self.fpr, self.tpr, self.roc_auc = self._run_roc_analysis()


    def _prepare_data_for_roc_analysis(self, predictions: Predictions) -> pd.DataFrame:
        results_per_slide = defaultdict(dict)
        
        # Average predictions of tiles to obtain one prediction per slide
        for slide_id in list(set(predictions.predictions['slide_id'].tolist())):
            slide_predictions = predictions.get_predictions_for_slide(slide_id)
            reference_value = predictions.get_reference_value_for_slide(slide_id)
            average_probability = np.average(slide_predictions, axis=0)

            if self.num_classes == 2: 
                positive = np.where(np.asarray(slide_predictions) >= 0.5, 1, 0)
                percentage_positive = np.average(positive, axis=0)
            else: 
                percentage_positive = float('NaN')
            
            results_per_slide[slide_id]['reference_value'] = reference_value
            results_per_slide[slide_id]['average_probability'] = average_probability
            results_per_slide[slide_id]['percentage_positive'] = percentage_positive
        
        # Turn results into pandas data frame
        result_df = pd.DataFrame(results_per_slide).T
        result_df.reset_index(inplace=True)
        result_df.rename({'index':'slide_id'}, axis='columns', inplace=True)

        return result_df


    def _run_roc_analysis(self) -> Tuple[dict, dict, dict]:
        
        # Multi-class ROC curve including ROC curve for each class-vs-rest, micro- and macro-average ROC, only for averaging method 'average_probability'
        if self.num_classes > 2: 
            fpr, tpr, roc_auc = self._generate_multiclass_roc_curves()

        # Two-class ROC curve, consider both averaging methods, i.e. average_probability and percentage_positive
        else: 
            fpr = {}
            tpr = {}
            roc_auc = {}
            reference = self.roc_data['reference_value'].tolist()
            fpr['average_probability'], tpr['average_probability'], roc_auc['average_probability'] = self._generate_roc_curve(reference, prediction=self.roc_data['average_probability'].tolist())
            fpr['percentage_positive'], tpr['percentage_positive'], roc_auc['percentage_positive'] = self._generate_roc_curve(reference, prediction=self.roc_data['percentage_positive'].tolist())
        
        return fpr, tpr, roc_auc


    def _generate_multiclass_roc_curves(self) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray], Dict[str, float]]: 
        # Binarize the reference values 
        reference = label_binarize(self.roc_data['reference_value'].tolist(), classes=[i for i in range(self.num_classes)])

        # Compute ROC curve and ROC area for each class vs. rest
        fpr = {}
        tpr = {}
        roc_auc = {}
        for i in range(self.num_classes):
            prediction = [x[i] for x in self.roc_data['average_probability']]
            fpr[i], tpr[i], roc_auc[i] = self._generate_roc_curve(reference[:, i], prediction)

        # Generate macro-average and micro-average ROC curve
        fpr['macro'], tpr['macro'], roc_auc['macro'] = self._generate_macro_average_roc(tpr, fpr)

        all_predictions = [i for x in result_df['average_probability'] for i in x]
        fpr['micro'], tpr['micro'], roc_auc['micro'] = self._generate_roc_curve(reference.ravel(), all_predictions)

        return fpr, tpr, roc_auc 


    def _generate_roc_curve(self, reference: List[int], prediction: List[int]) -> Tuple[np.ndarray, np.ndarray, float]:
        fpr, tpr, _ = roc_curve(
            y_true = reference,
            y_score = prediction
        )
        roc_auc = auc(fpr, tpr)
        return fpr, tpr, roc_auc


    def _generate_macro_average_roc(self, tpr: np.ndarray, fpr: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
        # Aggregate all false positive rates
        all_fpr = np.unique(np.concatenate([fpr[i] for i in range(3)]))

        # Interpolate true positive rate at the respective false positive rate
        mean_tpr = np.zeros_like(all_fpr)
        for i in range(3):
            mean_tpr += interp(all_fpr, fpr[i], tpr[i])
        mean_tpr = mean_tpr/self.num_classes  

        roc_auc = auc(all_fpr, mean_tpr)
        return all_fpr, mean_tpr, roc_auc


    def plot(self, output_path) -> None:
        # Plot bisector
        plt.plot(
            [0, 1],
            [0, 1],
            color='navy',
            linewidth=2,
            linestyle='--'
        )

        # Plot ROC curves
        colors = ['orange', 'aqua', 'red', 'yellowgreen', 'yellow', 'magenta', 'royalblue', 'green', 'burlywood', 'grey']
        averaging_method = 'avg_prob'
        for i, key in enumerate(self.fpr):
            if key == 'percentage_positive': 
                averaging_method = 'per_pos'
            plt.plot(
                self.fpr[key],
                self.tpr[key],
                color=colors[i],
                linewidth=2,
                label='%s [%s] (area = %0.2f)' % (key, averaging_method, self.roc_auc[key])
            )

        """ TODO: add class for multiclass roc curves """ 

        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver operating characteristic')
        plt.legend(loc='lower right')
        plt.savefig(output_path)
