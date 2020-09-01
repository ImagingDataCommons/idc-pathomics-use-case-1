import numpy as np
from evaluation.evaluation import per_slide_evaluation
from data.data_set import Dataset

if __name__ == '__main__':
    test_dataset = Dataset('/home/dschacherer/Schreibtisch/testdata_out/csv_test_norm_cancer.csv', num_classes=3)
    res=per_slide_evaluation('dummy', test_dataset)
    print(res)