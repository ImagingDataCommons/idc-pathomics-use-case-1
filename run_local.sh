#!/bin/bash

cd "$(dirname "$0")" # move to script directory

docker build -t idc-pathomics-use-case-1 .
docker run \
    --rm \
    -u $(id -u ${USER}):$(id -g ${USER}) \
    -p 8888:8888 \
    -v $(pwd):/idc-pathomics-use-case-1 \
    -v /home/dschacherer/Schreibtisch/testdata_in/:/input_data \
    -v /home/dschacherer/Schreibtisch/testdata_out/:/output_data \
    idc-pathomics-use-case-1 \
    --NotebookApp.password=sha1:e94a79bd53f4:2213431eb9752b66e1734ca81548c339c5eb127e

# to run all notebooks non-interactively and save the results, use
#docker run \
#    --rm \
#    -u $(id -u ${USER}):$(id -g ${USER}) \
#    -v SOMEPATH:/output_data \
#    --entrypoint jupyter \
#    idc-pathomics-use-case-1 \
#    nbconvert --execute --output-dir=/output_data src/*.ipynb

cd - > /dev/null # move back to previous directory
