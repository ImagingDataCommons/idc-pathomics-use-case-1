import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from collections import defaultdict
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize
from scipy import interp

class Predictions():
    
    def __init__(self, model=None, dataset=None, load_from=None):
        
        if load_from: 
            self.predictions = pd.read_json(load_from)
        
        else: 
            predictions_dict = {}
            for i, data_point in enumerate(dataset.data_points[:5]):
                slide_id = data_point.get_slide_id()
                if slide_id not in predictions_dict:
                    predictions_dict[i] = {
                        'slide_id': slide_id,
                        'tile_position': data_point.get_position(),
                        'reference_value': data_point.get_reference_value(),
                        'prediction': model.make_prediction(data_point).numpy()
                    }

            self.predictions = pd.DataFrame.from_dict(predictions_dict, orient='index')
            self.roc_data = None
    
    def save(self, path):
        df.to_json(path)
    
    
    def generate_heatmap_for_slide(self, slide_id, colormaps):
        # extract predictions and tile coordinates for the given slide
        pred = self.predictions.loc[self.predictions['slide_id'] == slide_id]['prediction'].tolist()
        coord = self.predictions.loc[self.predictions['slide_id'] == slide_id]['tile_position'].tolist()
        max_cols, max_rows = max([c[0] for c in coord]) + 1, max([c[1] for c in coord]) + 1
        
        # configure the colormaps 
        for cmap in colormaps:
            cmap.set_over(alpha=0)
            cmap.set_under(alpha=0)
        
        # create heatmap
        slide_heatmap = -1 * np.ones((max_rows, max_cols, 4))
        for c, p in zip(coord, pred):
            p = p.tolist()
            colormap_to_use = colormaps[p.index(max(p))]
            slide_heatmap[c[1], c[0], :] = colormap_to_use(max(p))
        
        return slide_heatmap
    
    
    def perform_roc_analysis(self):
        #check whether data are already prepared
        if not self.roc_data:
            self._prepare_data_for_roc_analysis()

        # Multi-class ROC curve including ROC curve for each class-vs-rest, micro- and macro-average ROC, only for averaging method 'average_probability'
        if self._get_num_classes() > 2: 
            fpr, tpr, roc_auc = self._generate_multiclass_roc_curves()
            self.plot_roc_curves(fig, fpr, tpr, roc_auc)
    
        # Two-class ROC curve, consider both averaging methods, i.e. average_probability and percentage_positive
        else: 
            fpr = {}
            tpr = {}
            roc_auc = {}
            reference = self.roc_data['reference_value'].tolist()
            fpr['average_probability'], tpr['average_probability'], roc_auc['average_probability'] = self._generate_roc_curve(reference, prediction=result_df['average_probability'].tolist())
            fpr['percentage_positive'], tpr['percentage_positive'], roc_auc['percentage_positive'] = self._generate_roc_curve(reference, prediction=result_df['percentage_positive'].tolist())
            self._plot_roc_curves(fig, fpr, tpr, roc_auc)
    
    
    def _prepare_data_for_roc_analysis(self):
        results_per_slide = defaultdict(dict)
        
        # average predictions of tiles to obtain one prediction per slide 
        for slide_id in set(self.predictions['slide_id'].tolist()):
            slide_predictions = np.array(self.predictions.loc[self.predictions['slide_id'] == slide_id]['prediction'].tolist())
            reference_value = self.predictions.loc[self.predictions['slide_id'] == slide_id]['reference_value'].tolist()[0]
            average_probability = np.average(slide_predictions, axis=0)

            if self._get_num_classes() == 2: 
                positive = np.where(slide_predictions >= 0.5, 1, 0)
                percentage_positive = np.average(positive, axis=0)
            else: 
                percentage_positive = float('NaN')
            
            results_per_slide[slide_id]['reference_value'] = reference_value
            results_per_slide[slide_id]['average_probability'] = average_probability
            results_per_slide[slide_id]['percentage_positive'] = percentage_positive

        # turn results into pandas data frame
        result_df = pd.DataFrame(results_per_slide)
        result_df.rename({'index':'slide_id'}, axis='columns', inplace=True)
        result_df.reset_index(drop=True, inplace=True)

        self.roc_data = result_df 

    
    def _generate_multiclass_roc_curves(self): 
        # Binarize the reference values 
        reference = label_binarize(self.roc_data['reference_value'].tolist(), classes=[i for i in range(3)])

        # Compute ROC curve and ROC area for each class vs. rest
        fpr = {}
        tpr = {}
        roc_auc = {}
        for i in range(3):
            prediction = [x[i] for x in self.roc_data['average_probability']]
            fpr[i], tpr[i], roc_auc[i] = self._generate_roc_curve(reference[:, i], prediction)

        # Generate macro-average and micro-average ROC curve
        fpr['macro'], tpr['macro'], roc_auc['macro'] = self._generate_macro_average_roc(tpr, fpr)

        all_predictions = [i for x in result_df['average_probability'] for i in x]
        fpr['micro'], tpr['micro'], roc_auc['micro'] = self._generate_roc_curve(reference.ravel(), all_predictions)

        return fpr, tpr, roc_auc 
    
    
    def _generate_roc_curve(self, reference, prediction):
        fpr, tpr, _ = roc_curve(
            y_true = reference,
            y_score = prediction
        )
        roc_auc = auc(fpr, tpr)
        return fpr, tpr, roc_auc


    def _generate_macro_average_roc(self, tpr, fpr):
        # Aggregate all false positive rates
        all_fpr = np.unique(np.concatenate([fpr[i] for i in range(3)]))

        # Interpolate true positive rate at the respective false positive rate
        mean_tpr = np.zeros_like(all_fpr)
        for i in range(num_classes):
            mean_tpr += interp(all_fpr, fpr[i], tpr[i])
        mean_tpr = mean_tpr/num_classes  

        roc_auc = auc(all_fpr, mean_tpr)
        return all_fpr, mean_tpr, roc_auc
    
    
    def plot_roc_curves(self, axes, fpr, tpr, roc_auc):
        # Plot bisector
        plt.plot(
            [0, 1],
            [0, 1],
            color='navy',
            linewidth=2,
            linestyle='--'
        )

        # Plot ROC curves
        colors = ['orange', 'royalblue', 'red', 'yellowgreen', 'yellow', 'magenta', 'aqua', 'green', 'burlywood', 'grey']
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
    
    
    def _get_num_classes(self):
        pred = self.predictions['prediction'].tolist()[0]
        if len(pred) == 1: 
            return 2
        else: 
            return len(pred)
