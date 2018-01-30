#!/usr/bin/env bash
SERVICE_IP=172.18.0.3
DB_IP=172.18.0.4
EVENT_STORE_IP=172.18.0.5
RABBITMQ_IP=172.18.0.6


docker run -d \
-v rabbit_db:/var/lib/rabbitmq/mnesia/rabbit@travlendar-rabbit \
--hostname travlendar-rabbit --name rabbitmq --ip ${RABBITMQ_IP} --net mynet123 rabbitmq:3


docker build -t accountservice . && docker run -d \
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
--name accountservice accountservice


docker run -it -d \
-e POSTGRES_USER='lpraat' \
-e POSTGRES_PASSWORD='password' \
-v accountservice_db:/var/lib/postgresql/data \
--ip ${DB_IP} \
--net mynet123 \
--name accountservice_db postgres:alpine


docker run -it -d \
-e POSTGRES_USER='lpraat' \
-e POSTGRES_PASSWORD='password' \
-v accountservice_event_store:/var/lib/postgresql/data \
--ip ${EVENT_STORE_IP} \
--net mynet123 \
--name accountservice_event_store postgres:alpine





docker run -it -d \
-e POSTGRES_USER='test' \
-e POSTGRES_PASSWORD='test' \
-v accountservice_test_db:/var/lib/postgresql/data \
-p 5433:5432 \
--name accountservice_db_test postgres:alpine

docker run -it -d \
-e POSTGRES_USER='test' \
-e POSTGRES_PASSWORD='test' \
-v accountservice_test_event_store:/var/lib/postgresql/data \
-p 5434:5432 \
--name accountservice_event_store_test postgres:alpine

docker run -d --hostname travlendar-rabbit-test -p 5672:5672 --name rabbitmq-test rabbitmq:3
