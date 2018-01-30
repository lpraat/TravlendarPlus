#!/usr/bin/env bash
SERVICE_IP=172.18.0.15
REDIS_IP=172.18.0.16

docker network create --subnet=172.18.0.0/16 mynet123

docker build -t computeservice . && docker run -d \
-e REDIS_IP=${REDIS_IP} \
-e REDIS_PORT='6379' \
--ip ${SERVICE_IP} \
--net mynet123 \
--name computeservice computeservice


docker run -it -d \
--ip ${REDIS_IP} \
--net mynet123 \
--name redis_server redis
