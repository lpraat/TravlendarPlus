#!/usr/bin/env bash
# add kong apis, in reverse order so that routing is done correctly.
# Run this inside the kong container -> kubectl cp kong_setup.sh default/kong-4148785002-97br6:/
# instructions
curl -i -X DELETE http://localhost:8001/apis/instructions
curl -i -X POST http://localhost:8001/apis/ \
	-d 'name=instructions' \
        -d 'upstream_url=http://ins.default.svc.cluster.local' \
        --data-urlencode 'uris=/users/\d+/calendars/\d+/events/\d+/recurrence/\d+/instruction,/users/\d+/calendars/\d+/events/\d+/recurrence/\d+/return' \
	-d 'strip_uri=false'
curl -i -X POST http://localhost:8001/apis/instructions/plugins --data "name=jwt"
# event
curl -i -X DELETE http://localhost:8001/apis/event
curl -i -X POST http://localhost:8001/apis/ \
	-d 'name=event' \
        -d 'upstream_url=http://ev.default.svc.cluster.local' \
        --data-urlencode 'uris=/users/\d+/calendars/\d+/events,/users/\d+/schedule' \
	-d 'strip_uri=false'
curl -i -X POST http://localhost:8001/apis/event/plugins --data "name=jwt"
# calendar
curl -i -X DELETE http://localhost:8001/apis/calendar
curl -i -X POST http://localhost:8001/apis/ \
	-d 'name=calendar' \
        -d 'upstream_url=http://cal.default.svc.cluster.local' \
        --data-urlencode 'uris=/users/\d+/calendars,/users/\d+/preferences' \
	-d 'strip_uri=false'
curl -i -X POST http://localhost:8001/apis/calendar/plugins --data "name=jwt"
# account
curl -i -X DELETE http://localhost:8001/apis/account
curl -i -X POST http://localhost:8001/apis/ \
	-d 'name=account' \
        -d 'upstream_url=http://acc.default.svc.cluster.local' \
        --data-urlencode 'uris=/users/\d+' \
	-d 'strip_uri=false'
curl -i -X POST http://localhost:8001/apis/account/plugins --data "name=jwt"
# login
curl -i -X DELETE http://localhost:8001/apis/login
curl -i -X POST http://localhost:8001/apis/ \
	-d 'name=login' \
        --data-urlencode 'upstream_url=http://acc.default.svc.cluster.local' \
        -d 'uris=/' \
	-d 'strip_uri=false'

# fix redis issue
docker exec -it redis_server redis-cli config set stop-writes-on-bgsave-error no
docker exec -it redis_server sysctl -p /etc/sysctl.conf
