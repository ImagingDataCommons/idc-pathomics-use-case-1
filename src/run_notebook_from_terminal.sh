#!/bin/bash

NOTEBOOK_NAME=$1

jupyter nbconvert --to=script --RegexRemovePreprocessor.patterns="['^\%']" --output-dir="./" "${NOTEBOOK_NAME}.ipynb"
screen -S experiment -dm bash -c "python ${NOTEBOOK_NAME}.py; exec sh"
