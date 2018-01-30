#!/usr/bin/env bash
SERVICE_IP=172.18.0.13
DB_IP=172.18.0.14
RABBITMQ_IP=172.18.0.6
COMPUTE_SERVICE_IP=172.18.0.15

docker network create --subnet=172.18.0.0/16 mynet123

docker build -t instructionsservice . && docker run -d \
-e DB_USER='postgres' \
-e DB_PASSWORD='admin' \
-e DB_IP=${DB_IP} \
-e DB_DB='production' \
-e DB_PORT='5432' \
-e RABBITMQ_IP=${RABBITMQ_IP} \
-e RABBITMQ_PORT='5672' \
-e COMPUTE_SERVICE_IP=${COMPUTE_SERVICE_IP} \
-e COMPUTE_SERVICE_PORT='8006' \
--ip ${SERVICE_IP} \
--net mynet123 \
--name instructionsservice instructionsservice

docker run -it -d \
-e POSTGRES_USER='postgres' \
-e POSTGRES_PASSWORD='admin' \
-e POSTGRES_DB='production' \
-v instructionsservice_db:/var/lib/postgresql/data \
--ip ${DB_IP} \
--net mynet123 \
--name instructionsservice_db postgres:alpine

docker run -d --hostname travlendar-rabbit --name rabbitmq --ip ${RABBITMQ_IP} --net mynet123 rabbitmq:3

docker run -it -d \
-e POSTGRES_USER='test' \
-e POSTGRES_PASSWORD='test' \
-e POSTGRES_DB='test' \
-v instructionsservice_test_db:/var/lib/postgresql/data \
-p 5434:5432 \
--name instructionsservice_db_test postgres:alpine

docker run -d --hostname travlendar-rabbit-test -p 5672:5672 --name rabbitmq-test rabbitmq:3
