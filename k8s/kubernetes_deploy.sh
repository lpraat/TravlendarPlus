# delete deployments and services for a clean startup
kubectl delete deployment --all
kubectl delete service --all

kubectl create -f ./yamls/rabbit/rabbit.yaml

kubectl create -f ./yamls/acc/accountservice_db.yaml
kubectl create -f ./yamls/acc/accountservice_event_store.yaml
kubectl create -f ./yamls/acc/accountservice.yaml

kubectl create -f ./yamls/cal/calendarservice_db.yaml
kubectl create -f ./yamls/cal/calendarservice_event_store.yaml
kubectl create -f ./yamls/cal/calendarservice.yaml

kubectl create -f ./yamls/ev/eventservice_event_store.yaml
kubectl create -f ./yamls/ev/eventservice_db.yaml
kubectl create -f ./yamls/ev/eventservice.yaml

kubectl create -f ./yamls/com/computeservice_redis.yaml
kubectl create -f ./yamls/com/computeservice.yaml

kubectl create -f ./yamls/ins/instructionsservice_db.yaml
kubectl create -f ./yamls/ins/instructionsservice.yaml

kubectl create -f ./yamls/kong/kong_postgres.yaml

# Runs a jon for the migrations, this job is deleted at the end of the script
kubectl create -f ./yamls/kong/kong_migration_postgres.yaml
kubectl create -f ./yamls/kong/kong_postgres.yaml


## TODO ##
# KONG SETUP LIKE IN KONG_SETUP.SH #
##     ##

kubectl delete -f ./yamls/kong/kong_migration_postgres.yaml
