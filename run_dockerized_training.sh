#!/bin/bash

cd "$(dirname "$0")" # move to script directory

docker build -t idc-pathomics-use-case-1 .

docker rm idc-pathomics-use-case-1-training

docker run \
    -it \
    --name idc-pathomics-use-case-1-training \
    --gpus all \
    -u $(id -u ${USER}):$(id -g ${USER}) \
    -v /home/dschacherer/idc_input:/input_data \
    -e "IDC_INPUT_DATA_DIR=/input_data" \
    -v /home/dschacherer/idc_output:/output_data \
    -e "IDC_OUTPUT_DATA_DIR=/output_data" \
    --entrypoint /bin/bash \
    idc-pathomics-use-case-1 \
    -c "jupyter nbconvert --to=script --output-dir=/tmp --RegexRemovePreprocessor.patterns=\"['^\%']\" training.ipynb ; PYTHONPATH=. python3 /tmp/training.py"

cd - > /dev/null # move back to previous directory