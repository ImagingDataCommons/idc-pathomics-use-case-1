#!/usr/bin/env bash

# Copyright (c) Fraunhofer MEVIS, Germany. All rights reserved.
# **InsertLicense** code

# TODO think about properly installing certificate and using it
env GIT_SSL_NO_VERIFY=true git clone https://clusterhelloworld-deploytoken:V-HTBDe_1QdthFedxsAE@gitlab.fme.lan/oschwen/clusterhelloworld.git /code
cd /code
git checkout "$1"

# in case you wish to remove the credentials in the container (e.g., to prevent it from appearing in sumatra records)
# sed -ie 's_https://.*gitlab.fme.lan_https://gitlab.fme.lan_' .git/config

/code/actualCode/_runInsideDocker.sh
