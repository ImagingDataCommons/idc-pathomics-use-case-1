import numpy as np
import pandas as pd 
import matplotlib.pyplot as plt
import seaborn as sns
from collections import defaultdict
from sklearn.metrics import roc_curve, auc, roc_auc_score
from sklearn.preprocessing import label_binarize
from sklearn.preprocessing import MultiLabelBinarizer
from scipy import interp
from itertools import chain
from typing import Tuple, List, Dict
pd.set_option("display.max_columns", None)


from evaluation.predictions import Predictions 

EXPERIMENTS = {'norm_cancer': {0: 'Normal', 1:'Tumor'}, 'luad_lusc': {0:'LUAD', 1:'LUSC'}, 'norm_luad_lusc': {0:'Normal', 1:'LUAD', 2:'LUSC'}, 
               'mutations': {0: 'STK11', 1: 'EGFR', 2: 'SETBP1', 3: 'TP53', 4: 'FAT1', 5: 'KRAS', 6: 'KEAP1', 7: 'LRP1B', 8: 'FAT4', 9: 'NF1'}}

class ROCAnalysis():

    def __init__(self, predictions: Predictions, experiment: str) -> None:
        self.experiment = experiment
        self.num_classes = len(EXPERIMENTS[experiment])
        
        # Tile-based analysis
        self.tile_roc_auc, self.tile_ci = self._run_tile_based_roc_analysis(predictions)
        # Slide-based analysis
        self.roc_data = self._prepare_data_for_slide_based_roc_analysis(predictions)
        self.fpr, self.tpr, self.roc_auc, self.ci = self._run_slide_based_roc_analysis()


    def _run_tile_based_roc_analysis(self, predictions: Predictions) -> Tuple[float, list):
        reference = []
        prediction = []
        all_slide_ids = list(set(predictions.predictions['slide_id'].tolist()))
        for slide_id in all_slide_ids: 
            reference.extend(predictions.get_all_reference_values_for_slide(slide_id))
            prediction.extend(predictions.get_predictions_for_slide(slide_id))
        reference = np.asarray(reference)
        prediction = np.asarray(prediction) 

        if self.num_classes == 2: 
            prediction = np.reshape(prediction, (1, -1)).squeeze()
            auc = [roc_auc_score(reference, prediction)]
            ci = self._get_confidence_interval_by_bootstrapping(reference, prediction)

        # Multi-class and multi-class multi-label data: Calculate AUC for each class separately      
        else: 
            reference = self._binarize_labels(reference)         
            auc = roc_auc_score(reference, prediction, average=None)
            for i in range(self.num_classes):
                ci = self._get_confidence_interval_by_bootstrapping(reference[:, i], prediction[:,i])
            
            if self.num_classes == 3: 
                pass 
                # ev. TODO: micro and macro ci
        
        return auc, ci


    def _get_confidence_interval_by_bootstrapping(self, reference: np.ndarray, prediction: np.ndarray, num_bootstraps: int = 1000) -> List[float]: 
        # TODO special case for macro ROC auc?! 
        bootstrap_scores = []

        for i in range(num_bootstraps):
            bootstrap_indices = np.random.randint(0, len(reference), size=len(reference))
            reference_sample = reference[bootstrap_indices]
            prediction_sample = prediction[bootstrap_indices]
            # We need at least one positive and one negative sample
            if len(np.unique(reference_sample)) < 2:
                continue
            else: 
                auc = roc_auc_score(reference_sample, prediction_sample)
                bootstrap_scores.append(auc)

        bootstrap_scores = np.asarray(bootstrap_scores)
        bootstrap_scores.sort()
        ci_lower = bootstrap_scores[int(0.025* len(bootstrap_scores))]
        ci_upper = bootstrap_scores[int(0.975* len(bootstrap_scores))]
        return [ci_lower, ci_upper]  


    def _prepare_data_for_slide_based_roc_analysis(self, predictions: Predictions) -> pd.DataFrame:
        results_per_slide = defaultdict(dict)

        # Average predictions of tiles to obtain one prediction per slide
        all_slide_ids = list(set(predictions.predictions['slide_id'].tolist()))
        for slide_id in all_slide_ids:
            slide_predictions = predictions.get_predictions_for_slide(slide_id)
            reference_value = predictions.get_reference_value_for_slide(slide_id)
            
            average_probability = np.average(slide_predictions, axis=0)
            positive = np.where(np.asarray(slide_predictions) >= 0.5, 1, 0)
            percentage_positive = np.average(positive, axis=0)

            results_per_slide[slide_id]['reference_value'] = reference_value
            results_per_slide[slide_id]['average_probability'] = average_probability
            results_per_slide[slide_id]['percentage_positive'] = percentage_positive
        
        # Turn results into pandas data frame: slide_id (str) | reference_value (int) | average_probability (list[int]) | percentage_positive (list[int]))
        # Note: In two-class problem, average_probability and percentage_positive contain only one value, otherwise correspondingly to the number of classes.
        result_df = pd.DataFrame(results_per_slide).T
        result_df.reset_index(inplace=True)
        result_df.rename({'index':'slide_id'}, axis='columns', inplace=True)
        print(result_df)
        return result_df


    def _run_slide_based_roc_analysis(self) -> Tuple[dict, dict, dict, dict]:
        
        # Multi-class ROC curve including ROC curve for each class-vs-rest, micro- and macro-average ROC, only for averaging method 'average_probability'
        if self.num_classes > 2: 
            fpr, tpr, roc_auc, ci = self._generate_multiclass_roc_curves()

        # Two-class ROC curve, consider both averaging methods, i.e. average_probability and percentage_positive
        else: 
            fpr = {}
            tpr = {}
            roc_auc = {}
            ci = {}
            reference = self.roc_data['reference_value'].tolist()
            for column in ['average_probability', 'percentage_positive']:
                prediction = np.concatenate(self.roc_data[column]).ravel()
                fpr[column], tpr[column], roc_auc[column] = self._generate_roc_curve(reference, prediction=self._ravel_helper(self.roc_data[column]))
                ci[column] = self._get_confidence_interval_by_bootstrapping(np.asarray(reference), prediction)
        
        return fpr, tpr, roc_auc, ci


    def _ravel_helper(self, list_of_arrays: List[np.ndarray]) -> np.ndarray:
        return np.concatenate(list_of_arrays).ravel()


    def _generate_multiclass_roc_curves(self) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray], Dict[str, float]]: 
        # Binarize the reference values 
        reference = self._binarize_labels(self.roc_data['reference_value'].tolist())

        # Compute ROC curve and ROC area for each class vs. rest
        fpr = defaultdict(dict)
        tpr = defaultdict(dict)
        roc_auc = defaultdict(dict)
        ci = defaultdict(dict)
        for i in range(self.num_classes):
            for column in ['percentage_positive', 'average_probability']:
                prediction = np.asarray([x[i] for x in self.roc_data[column]])
                fpr[column][i], tpr[column][i], roc_auc[column][i] = self._generate_roc_curve(reference[:, i], prediction)
                ci[column][i] = self._get_confidence_interval_by_bootstrapping(reference[:,i], prediction)

        # Generate macro-average and micro-average ROC curve for the three-class classification problem
        if self.num_classes == 3:
            for column in ['percentage_positive', 'average_probability']:
                fpr[column]['macro'], tpr[column]['macro'], roc_auc[column]['macro'] = self._generate_macro_average_roc(tpr[column], fpr[column])
                # TODO ci['macro] 

                all_predictions = np.asarray([i for x in self.roc_data[column] for i in x])
                fpr[column]['micro'], tpr[column]['micro'], roc_auc[column]['micro'] = self._generate_roc_curve(reference.ravel(), all_predictions)
                ci[column]['micro'] = self._get_confidence_interval_by_bootstrapping(reference.ravel(), all_predictions)

        print(roc_auc, ci)
        return fpr, tpr, roc_auc, ci


    def _binarize_labels(self, values: np.ndarray) -> np.ndarray:
        if self.num_classes == 10: # multi-label
            mlb = MultiLabelBinarizer(classes=[i for i in range(self.num_classes)])
            binarized = mlb.fit_transform(values)
        else: 
            binarized = label_binarize(values, classes=[i for i in range(self.num_classes)]) 
        return binarized


    def _generate_roc_curve(self, reference: np.ndarray, prediction: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
        print(reference, prediction, type(reference), type(prediction))
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
            color='black',
            linewidth=1,
            linestyle='--'
        )

        # Plot ROC curves
        colors = ['orange', 'aqua', 'red', 'yellowgreen', 'yellow', 'magenta', 'royalblue', 'green', 'burlywood', 'grey']
        for i, key in enumerate(self.fpr):
            if self.num_classes == 2:
                label='%s (AUC = %0.3f)' % (key, self.roc_auc[key])
            else:
                class_to_str_mapping = EXPERIMENTS[self.experiment]
                label='%s [avg_prob] (AUC = %0.3f)' % (class_to_str_mapping[key].upper(), self.roc_auc[key])
            plt.plot(
                self.fpr[key],
                self.tpr[key],
                color=colors[i],
                linewidth=2,
                label=label
            )

        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False positive rate')
        plt.ylabel('True positive rate')
        plt.title('Receiver operating characteristic')
        plt.legend(loc='lower right')
        plt.savefig(output_path)
        plt.close()
