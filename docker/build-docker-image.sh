#!/usr/bin/env bash

# Copyright (c) Fraunhofer MEVIS, Germany. All rights reserved.
# **InsertLicense** code

cd "$(dirname "$0")"

docker build -t oswe-clusterhelloworld:latest .
