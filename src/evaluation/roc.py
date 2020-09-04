import matplotlib.pyplot as plt
from sklearn.metrics import roc_curve, auc
from sklearn.preprocessing import label_binarize

def evaluate_by_roc_curve(fig, result_df):
    # Get number of classes
    if type(result_df['average_probability'][0]) != list:
        num_classes = 2
    else: 
        num_classes = len(result_df['average_probability'][0])

    # Multi-class ROC curve including ROC curve for each class-vs-rest, micro- and macro-average ROC
    if num_classes > 2: 
        fpr, tpr, roc_auc = generate_multiclass_roc_curves(result_df, num_classes)
        plot_roc_curves(fig, fpr, tpr, roc_auc)
    
    # Two-class ROC curve, consider both averaging methods, i.e. average_probability and percentage_positive
    else: 
        fpr = {}
        tpr = {}
        roc_auc = {}
        reference = result_df['reference_value'].tolist()
        fpr['average_probability'], tpr['average_probability'], roc_auc['average_probability'] = generate_roc_curve(reference, prediction=result_df['average_probability'].tolist())
        fpr['percentage_positive'], tpr['percentage_positive'], roc_auc['percentage_positive'] = generate_roc_curve(reference, prediction=result_df['percentage_positive'].tolist())
        plot_roc_curves(fig, fpr, tpr, roc_auc)


def generate_multiclass_roc_curves(result_df, num_classes): 
    # Binarize the reference values 
    reference = label_binarize(result_df['reference_value'].tolist(), classes=[i for i in range(num_classes)])

    # Compute ROC curve and ROC area for each class
    fpr = {}
    tpr = {}
    roc_auc = {}
    for i in range(num_classes):
        prediction = [x[i] for x in result_df['average_probability']]
        fpr[i], tpr[i], roc_auc[i] = generate_roc_curve(reference[:, i], prediction)
    
    # Generate micro-average and macro-average ROC curve
    all_predictions = [i for x in result_df['average_probability'] for i in x]
    fpr['micro'], tpr['micro'], roc_auc['micro'] = generate_roc_curve(reference.ravel(), all_predictions)
    
    # TODO generate_macro_average_roc()
    
    return fpr, tpr, roc_auc 


def generate_roc_curve(reference, prediction):
    fpr, tpr, _ = roc_curve(
        y_true = reference,
        y_score = prediction
    )
    roc_auc = auc(fpr, tpr)
    return fpr, tpr, roc_auc


def generate_macro_average_roc():
    """ TODO """ 
    pass 


def plot_roc_curves(axes, fpr, tpr, roc_auc):
    # Plot bisector
    plt.plot(
        [0, 1],
        [0, 1],
        color='navy',
        linewidth=2,
        linestyle='--'
    )

    # Plot ROC curves
    colors = ['orange', 'royalblue', 'red', 'yellowgreen', 'yellow', 'magenta', 'aqua', 'green', 'burlywood', 'black']
    averaging_method = 'avg_prob'
    for i, key in enumerate(fpr):
        if key == 'percentage_positive': 
            averaging_method = 'per_pos'
        plt.plot(
            fpr[key],
            tpr[key],
            color=colors[i],
            linewidth=2,
            label='ROC curve [%s] (area = %0.2f)' % (averaging_method, roc_auc[key])
        )
    
    """ TODO: add class for multiclass roc curves """ 

    plt.xlim([0.0, 1.0])
    plt.ylim([0.0, 1.05])
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title('Receiver operating characteristic')
    plt.legend(loc="lower right")
