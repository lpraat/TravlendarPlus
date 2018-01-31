## TODO ##
# KONG SETUP LIKE IN KONG_SETUP.SH #
##     ##



# Find the redis pod name
redis_pod=$(kubectl get pods | grep com-redis | awk '{print $1}')

kubectl exec $redis_pod redis-cli config set stop-writes-on-bgsave-error no
#kubectl exec $redis_pod sysctl -p /etc/sysctl.conf
