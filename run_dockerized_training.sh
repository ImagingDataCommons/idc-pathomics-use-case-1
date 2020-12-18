#!/bin/bash

cd "$(dirname "$0")" # move to script directory

docker build -t idc-pathomics-use-case-1 .

docker rm idc-pathomics-use-case-1-training

COMMIT=$(git rev-parse --short HEAD)
if ! git diff-index --quiet HEAD --
then
    COMMIT="${COMMIT}_modified"
fi

INTERACTIVE=false
for arg in "$@" 
do 
    case $arg in 
        -i|--interactive)
        INTERACTIVE=true
        shift 
        ;;
    esac
done

if [ "$INTERACTIVE" = false ] # run docker non-interactively
then
    docker run \
        -it \
        --name idc-pathomics-use-case-1-training \
        --gpus all \
        -u $(id -u ${USER}):$(id -g ${USER}) \
        -v ${IDC_PATHOMICS_USE_CASE_1_INPUT_DATA_DIR}:/input_data \
        -e "IDC_INPUT_DATA_DIR=/input_data" \
        -v ${IDC_PATHOMICS_USE_CASE_1_OUTPUT_DATA_DIR}:/output_data \
        -e "IDC_OUTPUT_DATA_DIR=/output_data" \
        -e "GIT_COMMIT=${COMMIT}" \
        idc-pathomics-use-case-1 
        -c "jupyter nbconvert --to=script --output-dir=/tmp --RegexRemovePreprocessor.patterns=\"['^\%']\" training.ipynb ; PYTHONPATH=. python3 /tmp/training.py"
else # run docker interactively
    docker run \
        -it \
        -p "8888:8888" \
        --name idc-pathomics-use-case-1-training \
        --gpus all \
        -u $(id -u ${USER}):$(id -g ${USER}) \
        -v /home/dschacherer/idc_input:/input_data \
        -e "IDC_INPUT_DATA_DIR=/input_data" \
        -v /home/dschacherer/idc_output:/output_data \
        -e "IDC_OUTPUT_DATA_DIR=/output_data" \
        -e "GIT_COMMIT=${COMMIT}" \
        idc-pathomics-use-case-1
fi 

cd - > /dev/null # move back to previous directory
