from sklearn.metrics import roc_curve, auc

# for now only works with binary classification results
def generate_roc_curve(result_df, prediction_column, positive_value=None):
    fpr, tpr, _ = roc_curve(
        y_true = result_df['reference_value'],
        y_score = result_df[prediction_column],
        pos_label=positive_value
    )
    roc_auc = auc(fpr, tpr)
    return fpr, tpr, roc_auc

def plot_roc_curve(axes, result_df, prediction_column, positive_value=None):
    fpr, tpr, roc_auc = generate_roc_curve(result_df, prediction_column, positive_value)

    axes.plot(
        fpr,
        tpr,
        color='darkorange',
        linewidth=2,
        label='ROC curce (area = %0.2f)' % roc_auc
    )
    axes.plot(
        [0, 1],
        [0, 1],
        color='navy',
        linewidth=2,
        linestyle='--'
    )
    axes.set_xlim([0.0, 1.0])
    axes.set_ylim([0.0, 1.05])
    axes.set_xlabel('False Positive Rate')
    axes.set_ylabel('True Positive Rate')
    axes.set_title('Receiver operating characteristic for "%s"' % prediction_column)
    axes.legend(loc="lower right")