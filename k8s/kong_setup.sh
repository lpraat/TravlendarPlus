#!/usr/bin/env bash

# add kong apis, in reverse order so that routing is done correctly

# instructions
kubectl exec $2 -- bash -c "curl -i -X DELETE http://$1/apis/instructions"
kubectl exec $2 -- bash -c "curl -i -X POST http://$1/apis/ \
	-d 'name=instructions' \
        -d 'upstream_url=http://ins.default.svc.cluster.local' \
        --data-urlencode 'uris=/users/\d+/calendars/\d+/events/\d+/recurrence/\d+/instruction,/users/\d+/calendars/\d+/events/\d+/recurrence/\d+/return' \
	-d 'strip_uri=false'"
kubectl exec $2 -- bash -c "curl -i -X POST http://$1/apis/instructions/plugins --data \"name=jwt\""

# event
kubectl exec $2 -- bash -c "curl -i -X DELETE http://$1/apis/event"
kubectl exec $2 -- bash -c "curl -i -X POST http://$1/apis/ \
	-d 'name=event' \
        -d 'upstream_url=http://ev.default.svc.cluster.local' \
        --data-urlencode 'uris=/users/\d+/calendars/\d+/events,/users/\d+/schedule' \
	-d 'strip_uri=false'"
kubectl exec $2 -- bash -c "curl -i -X POST http://$1/apis/event/plugins --data \"name=jwt\""

# calendar
kubectl exec $2 -- bash -c "curl -i -X DELETE http://$1/apis/calendar"
kubectl exec $2 -- bash -c "curl -i -X POST http://$1/apis/ \
	-d 'name=calendar' \
        -d 'upstream_url=http://cal.default.svc.cluster.local' \
        --data-urlencode 'uris=/users/\d+/calendars,/users/\d+/preferences' \
	-d 'strip_uri=false'"
kubectl exec $2 -- bash -c "curl -i -X POST http://$1/apis/calendar/plugins --data \"name=jwt\""

# account
kubectl exec $2 -- bash -c "curl -i -X DELETE http://$1/apis/account"
kubectl exec $2 -- bash -c "curl -i -X POST http://$1/apis/ \
	-d 'name=account' \
        -d 'upstream_url=http://acc.default.svc.cluster.local' \
        --data-urlencode 'uris=/users/\d+' \
	-d 'strip_uri=false'"
kubectl exec $2 -- bash -c "curl -i -X POST http://$1/apis/account/plugins --data \"name=jwt\""

# login
kubectl exec $2 -- bash -c "curl -i -X DELETE http://$1/apis/login"
kubectl exec $2 -- bash -c "curl -i -X POST http://$1/apis/ \
	-d 'name=login' \
        --data-urlencode 'upstream_url=http://acc.default.svc.cluster.local' \
        -d 'uris=/' \
	-d 'strip_uri=false'"



# Find the redis pod name
redis_pod=$(kubectl get pods | grep com-redis | awk '{print $1}')

kubectl exec $redis_pod redis-cli config set stop-writes-on-bgsave-error no
#kubectl exec $redis_pod sysctl -p /etc/sysctl.conf
# fix redis issue
