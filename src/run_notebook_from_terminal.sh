#!/bin/bash

NOTEBOOK=$1
OUTPUT_DIR=$2

screen -S experiment -dm bash -c "jupyter nbconvert --execute --to=script --output-dir=${OUTPUT_DIR} --ExecutePreprocessor.enabled=True --ExecutePreprocessor.timeout=-1 --ExecutionPreprocessor.allow_errors=True --allow-errors --Application.log_level=10 ${NOTEBOOK}; exec sh"
