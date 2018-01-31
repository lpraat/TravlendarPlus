redis_pod=$(kubectl get pods | grep com-redis | awk '{print $1}')

kubectl exec $redis_pod redis-cli config set stop-writes-on-bgsave-error no
