#!/usr/bin/env bash

# Copyright (c) Fraunhofer MEVIS, Germany. All rights reserved.
# **InsertLicense** code

SCRIPT_DIR="$(dirname "$(readlink -fm "$0")")"

$SCRIPT_DIR/helloWorld.py 2>&1 | tee "/output/console.out"
