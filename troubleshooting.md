# Troubleshooting journal

Keep chronological entries. Copy this block for each meaningful investigation.

## Entry / date / time

- Symptom: Both app-01 and app-02 were running but reported as unhealthy.
- Hypothesis: The Docker health check may be calling an endpoint that the Flask application does not provide.
- Command or test: `grep -R "@app.*health\|def health\|/health" -n app`; `docker compose -p barq-assessment ps -a`; `docker inspect --format='{{json .State.Health}}' app-01`
- Actual output: The Flask application defines `/health`. Both app containers were `unhealthy`. The health-check log showed `HTTP Error 404: NOT FOUND` repeatedly.
- Failed attempt and what changed your thinking: No failed attempt. The investigation confirmed the hypothesis.
- Root cause:
- Fix:
- Retest evidence:
- Related commit:
- Remaining uncertainty:


## Entry / date / time

- Symptom: A request through NGINX from the host produced an empty reply.
- Hypothesis: NGINX may be forwarding traffic to an incorrect application port.
- Command or test: `cat nginx/nginx.conf`; `docker exec nginx sh -c 'wget -qO- http://app-01:8081/health || echo "app-01:8081 FAILED"'`
- Actual output: NGINX configuration sends app-01 traffic to `app-01:8081`. The direct test returned `app-01:8081 FAILED` and `Connection refused`.
- Failed attempt and what changed your thinking: No failed attempt. The direct upstream test confirmed the hypothesis.
- Root cause:
- Fix:
- Retest evidence:
- Related commit:
- Remaining uncertainty:


## Entry / date / time

- Symptom: app-02 reports the same instance identity as app-01.
- Hypothesis: app-02 may be configured with the wrong INSTANCE_ID.
- Command or test: `docker exec app-02 python -c "import urllib.request; print(urllib.request.urlopen('http://127.0.0.1:8080/health').read().decode())"`; `grep -n "INSTANCE_ID" docker-compose.yml`
- Actual output: app-02 returned `"instance_id":"app-01"`. The Compose configuration contains `INSTANCE_ID: "app-01"` for both app-01 and app-02.
- Failed attempt and what changed your thinking: No failed attempt. The runtime response and configuration confirmed the hypothesis.
- Root cause:
- Fix:
- Retest evidence:
- Related commit:
- Remaining uncertainty:


## Entry / date / time

- Symptom: NGINX cannot connect to app-02 on port 8080, even though app-02 responds to requests made from inside its own container.
- Hypothesis: Flask is listening only on the container's loopback address instead of an address reachable by other containers.
- Command or test: `grep -n "APP_HOST\|APP_PORT" docker-compose.yml`
- Actual output: `APP_HOST` is configured as `127.0.0.1` and `APP_PORT` as `8080`.
- Failed attempt and what changed your thinking: The direct request from inside app-02 succeeded, while the request from the NGINX container to app-02:8080 was refused. This supports the loopback-binding hypothesis.
- Root cause:
- Fix:
- Retest evidence:
- Related commit:
- Remaining uncertainty:


## Entry / date / time

- Symptom: The PostgreSQL named volume is not mounted at the PostgreSQL data directory.
- Hypothesis: The database's actual data directory may be using temporary storage instead of the required named volume.
- Command or test: `grep -n "postgres-data\|/var/lib/postgresql" docker-compose.yml`; `docker inspect postgres --format='{{json .Mounts}}'`
- Actual output: The named volume `barq-assessment_postgres-data` is mounted at `/var/lib/postgresql/backup`, while `/var/lib/postgresql/data` is configured as temporary storage.
- Failed attempt and what changed your thinking: No failed attempt. The Compose configuration and runtime mount information confirmed the hypothesis.
- Root cause:
- Fix:
- Retest evidence:
- Related commit:
- Remaining uncertainty:


## Entry / date / time

- Symptom: PostgreSQL and Redis are published on host ports in addition to NGINX.
- Hypothesis: The Compose configuration exposes backend services directly to the host, contrary to the required network isolation.
- Command or test: `grep -n "ports:" -A1 docker-compose.yml`
- Actual output: PostgreSQL publishes `127.0.0.1:15432:5432`, Redis publishes `127.0.0.1:16379:6379`, and NGINX publishes `127.0.0.1:${PUBLIC_PORT:-8080}:81`.
- Failed attempt and what changed your thinking: No failed attempt. The configuration directly confirmed the hypothesis.
- Root cause:
- Fix:
- Retest evidence:
- Related commit:
- Remaining uncertainty:


## Entry / date / time

- Symptom: NGINX can establish TCP connections directly to both PostgreSQL and Redis.
- Hypothesis: The current network configuration allows NGINX to reach backend data services directly.
- Command or test: `docker exec nginx sh -c 'nc -zv postgres 5432'`; `docker exec nginx sh -c 'nc -zv redis 6379'`
- Actual output: PostgreSQL port 5432 was reported as open, and Redis port 6379 was reported as open from the NGINX container.
- Failed attempt and what changed your thinking: The first HTTP-based test was inconclusive because PostgreSQL and Redis are not HTTP services. TCP tests using `nc` confirmed that both ports are reachable.
- Root cause:
- Fix:
- Retest evidence:
- Related commit:
- Remaining uncertainty:


## Entry / date / time

- Symptom: NGINX can reach PostgreSQL and Redis directly over the backend network.
- Hypothesis: NGINX is attached to the same backend network as the database and cache.
- Command or test: `grep -n "networks:" -A8 docker-compose.yml`
- Actual output: NGINX is configured with `[frontend, backend]`. PostgreSQL and Redis are configured with `[backend]`. The backend network is marked `internal: true`.
- Failed attempt and what changed your thinking: No failed attempt. The network configuration explains the successful TCP connectivity tests.
- Root cause:
- Fix:
- Retest evidence:
- Related commit:
- Remaining uncertainty:


## Entry / date / time

- Symptom: The Flask application container runs as the root user.
- Hypothesis: The Dockerfile creates a non-root `app` user but later switches back to `root`.
- Command or test: `cat Dockerfile`; `docker exec app-01 whoami`
- Actual output: The Dockerfile contains `USER root`, and the running app-01 container reports `root`.
- Failed attempt and what changed your thinking: No failed attempt. The Dockerfile and runtime check confirmed the finding.
- Root cause:
- Fix:
- Retest evidence:
- Related commit:
- Remaining uncertainty:
