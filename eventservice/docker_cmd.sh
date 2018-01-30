#!/usr/bin/env bash
SERVICE_IP=172.18.0.10
DB_IP=172.18.0.11
EVENT_STORE_IP=172.18.0.12
RABBITMQ_IP=172.18.0.6

docker network create --subnet=172.18.0.0/16 mynet123

docker build -t eventservice . && docker run -d \
-e DB_USER='lpraat' \
-e DB_PASSWORD='password' \
-e DB_IP=${DB_IP} \
-e DB_DB='lpraat' \
-e DB_PORT='5432' \
-e EVENT_STORE_USER='lpraat' \
-e EVENT_STORE_PASSWORD='password' \
-e EVENT_STORE_IP=${EVENT_STORE_IP} \
-e EVENT_STORE_DB='lpraat' \
-e EVENT_STORE_PORT='5432' \
-e RABBITMQ_IP=${RABBITMQ_IP} \
-e RABBITMQ_PORT='5672' \
--ip ${SERVICE_IP} \
--net mynet123 \
--name eventservice eventservice


docker run -it -d \
-e POSTGRES_USER='lpraat' \
-e POSTGRES_PASSWORD='password' \
-v eventservice_db:/var/lib/postgresql/data \
--ip ${DB_IP} \
--net mynet123 \
--name eventservice_db postgres:alpine


docker run -it -d \
-e POSTGRES_USER='lpraat' \
-e POSTGRES_PASSWORD='password' \
-v eventservice_event_store:/var/lib/postgresql/data \
--ip ${EVENT_STORE_IP} \
--net mynet123 \
--name eventservice_event_store postgres:alpine



docker run -it -d \
-e POSTGRES_USER='test' \
-e POSTGRES_PASSWORD='test' \
-v eventservice_test_db:/var/lib/postgresql/data \
-p 5436:5432 \
--name eventservice_db_test postgres:alpine

docker run -it -d \
-e POSTGRES_USER='test' \
-e POSTGRES_PASSWORD='test' \
-v eventservice_test_event_store:/var/lib/postgresql/data \
-p 5437:5432 \
--name eventservice_event_store_test postgres:alpine
