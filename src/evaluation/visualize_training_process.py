import os 
import sys
import matplotlib.pyplot as plt 
import pandas as pd


if __name__ == '__main__': 
    train_file = sys.argv[1]
    train_data = pd.read_csv(train_file)
    plt.plot(train_data['loss'], label='training')
    plt.plot(train_data['val_loss'], label='validation')
    plt.xlabel('epoch')
    plt.ylabel('loss')
    plt.legend()
    plt.savefig(os.path.join(os.path.dirname(train_file), 'training_loss.png'))
    plt.close()
    plt.plot(train_data['auc'], label='training')
    plt.plot(train_data['val_auc'], label='validation')
    plt.xlabel('epoch')
    plt.ylabel('accuracy')
    plt.legend()
    plt.savefig(os.path.join(os.path.dirname(train_file), 'training_acc.png'))