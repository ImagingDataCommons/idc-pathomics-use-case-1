#!/bin/bash

cd "$(dirname "$0")" # move to script directory

docker build -t idc-pathomics-use-case-1 .
docker run \
    --rm \
    -u $(id -u ${USER}):$(id -g ${USER}) \
    -p 8888:8888 \
    -v $(pwd):/idc-pathomics-use-case-1 \
    idc-pathomics-use-case-1 \
    --NotebookApp.password=sha1:e94a79bd53f4:2213431eb9752b66e1734ca81548c339c5eb127e

cd - > /dev/null # move back to previous directory