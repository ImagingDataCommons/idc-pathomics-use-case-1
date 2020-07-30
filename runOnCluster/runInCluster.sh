#!/bin/bash

# Copyright (c) Fraunhofer MEVIS, Germany. All rights reserved.
# **InsertLicense** code

cd "$(dirname "$0")"

# get revision short ID if provided (as ID, tag, branch, …), otherwise use HEAD of master
# note: this may need to be passed from the calling script, if any
if [ "$#" -eq 1 ]
then
  COMMIT=$(git rev-parse --short $1)
else
  # use current local head
  COMMIT=$(git rev-parse --short HEAD)
fi

# prepare nomad job
TEMP_HCL_FILE=$(mktemp --suffix=.hcl)
cp clusterJob.hcl ${TEMP_HCL_FILE}
sed -i "s/PLACEHOLDER_COMMIT/${COMMIT}/g" ${TEMP_HCL_FILE}

# run nomad job
nomad run -address=http://cluster-master-pri.fme.lan:4646 -detach ${TEMP_HCL_FILE}

# clean up
rm ${TEMP_HCL_FILE}
