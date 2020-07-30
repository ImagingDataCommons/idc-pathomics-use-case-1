#!/usr/bin/env bash

# Copyright (c) Fraunhofer MEVIS, Germany. All rights reserved.
# **InsertLicense** code

# synchronize with gitlab
cd "$(dirname "$0")"
git pull
git push

# you may need to adapt the namespace to where you have write access
docker rmi registry.fme.lan/oschwen/oswe-clusterhelloworld:latest
docker tag oswe-clusterhelloworld:latest registry.fme.lan/cluster_hello_world/oswe-clusterhelloworld:latest
docker push registry.fme.lan/cluster_hello_world/oswe-clusterhelloworld:latest

./runInCluster.sh
