#!/usr/bin/env bash

# Removes all containers for a clean startup
docker rm -f $(docker ps -a -q)

# Removes all the docker volumes for a clean startup
docker stop accountservice_db
docker rm accountservice_db
docker volume rm accountservice_db

docker stop accountservice_event_store
docker rm accountservice_event_store
docker volume rm accountservice_event_store


docker stop calendarservice_db
docker rm calendarservice_db
docker volume rm calendarservice_db

docker stop calendarservice_event_store
docker rm calendarservice_event_store
docker volume rm calendarservice_event_store

docker stop eventservice_db
docker rm eventservice_db
docker volume rm eventservice_db

docker stop eventservice_event_store
docker rm eventservice_event_store
docker volume rm eventservice_event_store


docker stop instructionsservice_db
docker rm instructionsservice_db
docker volume rm instructionsservice_db

docker stop rabbitmq
docker rm rabbitmq
docker volume rm rabbit_db

# create subnet for static ip assignment
docker network create --subnet=172.18.0.0/16 mynet123
# create kong database

docker run -d --name kong-database \
              -p 5440:5432 \
              -e "POSTGRES_USER=kong" \
              -e "POSTGRES_DB=kong" \
	      --net mynet123 \
	      --ip "172.18.0.20" \
	      postgres:9.4

cd ./accountservice
bash ./docker_cmd.sh
cd ../calendarservice
bash ./docker_cmd.sh
cd ../eventservice
bash ./docker_cmd.sh
cd ../instructionsservice
bash ./docker_cmd.sh
cd ../computeservice
bash ./docker_cmd.sh

docker restart accountservice calendarservice eventservice instructionsservice computeservice

# run migrations for kong container and run it

docker run --rm \
    --link kong-database:kong-database \
    -e "KONG_DATABASE=postgres" \
    -e "KONG_PG_HOST=kong-database" \
    -e "KONG_CASSANDRA_CONTACT_POINTS=kong-database" \
    --net mynet123 \
    kong:latest kong migrations up

docker run -d --name kong \
    --link kong-database:kong-database \
    -e "KONG_DATABASE=postgres" \
    -e "KONG_PG_HOST=kong-database" \
    -e "KONG_CASSANDRA_CONTACT_POINTS=kong-database" \
    -e "KONG_PROXY_ACCESS_LOG=/dev/stdout" \
    -e "KONG_ADMIN_ACCESS_LOG=/dev/stdout" \
    -e "KONG_PROXY_ERROR_LOG=/dev/stderr" \
    -e "KONG_ADMIN_ERROR_LOG=/dev/stderr" \
    -p 8000:8000 \
    -p 8443:8443 \
    -p 8001:8001 \
    -p 8444:8444 \
    --net mynet123 \
    --ip "172.18.0.2" \
    kong:latest
