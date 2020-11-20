#!/bin/bash

NOTEBOOK=$1
OUTPUT_DIR=$2

jupyter nbconvert --execute --to=markdown --output-dir=$OUTPUT_DIR --ExecutePreprocessor.enabled=True --ExecutePreprocessor.timeout=-1 --ExecutionPreprocessor.allow_errors=True --allow-errors --Application.log_level=10 $NOTEBOOK