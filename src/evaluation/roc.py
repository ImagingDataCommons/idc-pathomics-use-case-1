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


def perform_roc_analysis(predictions: Predictions, num_classes: int) -> None:
    # Check whether data are already prepared TODO and verify that num_classes is allowed
    roc_data = _prepare_data_for_roc_analysis(predictions, num_classes)
    
    # Multi-class ROC curve including ROC curve for each class-vs-rest, micro- and macro-average ROC, only for averaging method 'average_probability'
    if num_classes > 2: 
        fpr, tpr, roc_auc = generate_multiclass_roc_curves()
        plot_roc_curves(fig, fpr, tpr, roc_auc)

    # Two-class ROC curve, consider both averaging methods, i.e. average_probability and percentage_positive
    else: 
        fpr = {}
        tpr = {}
        roc_auc = {}
        reference = roc_data['reference_value'].tolist()
        fpr['average_probability'], tpr['average_probability'], roc_auc['average_probability'] = _generate_roc_curve(reference, prediction=roc_data['average_probability'].tolist())
        fpr['percentage_positive'], tpr['percentage_positive'], roc_auc['percentage_positive'] = _generate_roc_curve(reference, prediction=roc_data['percentage_positive'].tolist())
    
    plot_roc_curves(fpr, tpr, roc_auc)


def _prepare_data_for_roc_analysis(predictions: Predictions, num_classes: int) -> pd.DataFrame:
    results_per_slide = defaultdict(dict)
    
    # average predictions of tiles to obtain one prediction per slide 
    for slide_id in set(predictions['slide_id'].tolist()):
        slide_predictions = predictions.get_predictions_for_slide(slide_id)
        reference_value = predictions.get_reference_value_for_slide(slide_id)
        average_probability = np.average(slide_predictions, axis=0)

        if num_classes == 2: 
            positive = np.where(slide_predictions >= 0.5, 1, 0)
            percentage_positive = np.average(positive, axis=0)
        else: 
            percentage_positive = float('NaN')
        
        results_per_slide[slide_id]['reference_value'] = reference_value
        results_per_slide[slide_id]['average_probability'] = average_probability
        results_per_slide[slide_id]['percentage_positive'] = percentage_positive
    
    # turn results into pandas data frame
    result_df = pd.DataFrame(results_per_slide).T
    result_df.reset_index(inplace=True)
    result_df.rename({'index':'slide_id'}, axis='columns', inplace=True)

    return result_df


def _generate_multiclass_roc_curves(roc_data: pd.DataFrame) -> Tuple[Dict[str, np.ndarray], Dict[str, np.ndarray], Dict[str, float]]: 
    # Binarize the reference values 
    reference = label_binarize(roc_data['reference_value'].tolist(), classes=[i for i in range(3)])

    # Compute ROC curve and ROC area for each class vs. rest
    fpr = {}
    tpr = {}
    roc_auc = {}
    for i in range(3):
        prediction = [x[i] for x in roc_data['average_probability']]
        fpr[i], tpr[i], roc_auc[i] = _generate_roc_curve(reference[:, i], prediction)

    # Generate macro-average and micro-average ROC curve
    fpr['macro'], tpr['macro'], roc_auc['macro'] = _generate_macro_average_roc(tpr, fpr)

    all_predictions = [i for x in result_df['average_probability'] for i in x]
    fpr['micro'], tpr['micro'], roc_auc['micro'] = _generate_roc_curve(reference.ravel(), all_predictions)

    return fpr, tpr, roc_auc 


def _generate_roc_curve(reference: List[int], prediction: List[int]) -> Tuple[np.ndarray, np.ndarray, float]:
    fpr, tpr, _ = roc_curve(
        y_true = reference,
        y_score = prediction
    )
    roc_auc = auc(fpr, tpr)
    return fpr, tpr, roc_auc


def _generate_macro_average_roc(tpr: np.ndarray, fpr: np.ndarray) -> Tuple[np.ndarray, np.ndarray, float]:
    # Aggregate all false positive rates
    all_fpr = np.unique(np.concatenate([fpr[i] for i in range(3)]))

    # Interpolate true positive rate at the respective false positive rate
    mean_tpr = np.zeros_like(all_fpr)
    for i in range(3):
        mean_tpr += interp(all_fpr, fpr[i], tpr[i])
    mean_tpr = mean_tpr/num_classes  

    roc_auc = auc(all_fpr, mean_tpr)
    return all_fpr, mean_tpr, roc_auc


def _plot_roc_curves(fpr: dict, tpr: dict, roc_auc: dict):
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
    for i, key in enumerate(fpr):
        if key == 'percentage_positive': 
            averaging_method = 'per_pos'
        plt.plot(
            fpr[key],
            tpr[key],
            color=colors[i],
            linewidth=2,
            label='%s [%s] (area = %0.2f)' % (key, averaging_method, roc_auc[key])
        )

    """ TODO: add class for multiclass roc curves """ 

    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic')
    plt.legend(loc="lower right")
