#!/bin/bash

NOTEBOOK_NAME=$1
SAVE_STOUT_STERR=$2

jupyter nbconvert --to=script --RegexRemovePreprocessor.patterns="['^\%']" --output-dir="./" "${NOTEBOOK_NAME}.ipynb"
screen -S experiment -dm bash -c "python ${NOTEBOOK_NAME}.py > ${SAVE_STOUT_STERR}/stdout.txt 2> ${SAVE_STOUT_STERR}/stderr.txt; exec sh"
