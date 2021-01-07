import os 
import sys
import matplotlib.pyplot as plt 
import pandas as pd


if __name__ == '__main__': 
    train_file = sys.argv[1]
    train_data = pd.read_csv(train_file)
    plt.plot(train_data['loss'])
    plt.plot(train_data['val_loss'])
    plt.savefig('/home/dschacherer/Schreibtisch/test.png')