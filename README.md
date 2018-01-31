## Instructions for deploying everything

- `git clone $this_repo`
- `cd k8s/`
- `sh kubernetes_deploy.sh`
- Copy the kong_setup.sh script inside the kong pod(KONG_POD='kong pod name assigned by kubernetes'):<br />
    `kubectl cp kong_setup.sh default/$KONG_POD:/`
- Run the script inside the kong pod: <br />
    `kubectl exec $KONG_POD -it bash` and
    `sh kong_setup.sh`
- Exit from the pod:<br />
    `exit`
- Get the external Travlendar ip address for the kong Proxy:<br />
    `kubectl get services | grep kong`
- Done
