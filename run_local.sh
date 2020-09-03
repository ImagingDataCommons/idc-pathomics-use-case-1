#!/bin/bash

cd "$(dirname "$0")" # move to script directory

export IDC_PATHOMICS_USE_CASE_1_INPUT_DATA_DIR='/home/dschacherer/Schreibtisch/testdata_in'
export IDC_PATHOMICS_USE_CASE_1_OUTPUT_DATA_DIR='/home/dschacherer/Schreibtisch/testdata_out'

# check directories for mounting are set and convert to absolute path
( [ -d "$IDC_PATHOMICS_USE_CASE_1_INPUT_DATA_DIR" ] && [ -d "$IDC_PATHOMICS_USE_CASE_1_OUTPUT_DATA_DIR" ] ) || \
    { echo "Invalid directory in environment variable IDC_PATHOMICS_USE_CASE_1_INPUT_DATA_DIR or IDC_PATHOMICS_USE_CASE_1_OUTPUT_DATA_DIR"; exit 1; }
IDC_PATHOMICS_USE_CASE_1_INPUT_DATA_DIR=$(readlink -m ${IDC_PATHOMICS_USE_CASE_1_INPUT_DATA_DIR})
IDC_PATHOMICS_USE_CASE_1_OUTPUT_DATA_DIR=$(readlink -m ${IDC_PATHOMICS_USE_CASE_1_OUTPUT_DATA_DIR})

docker build -t idc-pathomics-use-case-1 .

docker run \
    --rm \
    -u $(id -u ${USER}):$(id -g ${USER}) \
    -p 8888:8888 \
    -v $(pwd):/idc-pathomics-use-case-1 \
    -v ${IDC_PATHOMICS_USE_CASE_1_INPUT_DATA_DIR}:/input \
    -v ${IDC_PATHOMICS_USE_CASE_1_OUTPUT_DATA_DIR}:/output \
    idc-pathomics-use-case-1 \
    --NotebookApp.password=sha1:e94a79bd53f4:2213431eb9752b66e1734ca81548c339c5eb127e

# to run all notebooks non-interactively and save the results, use
#docker run \
#    --rm \
#    -u $(id -u ${USER}):$(id -g ${USER}) \
#    -v SOMEPATH:/output \
#    --entrypoint jupyter \
#    idc-pathomics-use-case-1 \
#    nbconvert --execute --output-dir=/output src/*.ipynb

cd - > /dev/null # move back to previous directory
