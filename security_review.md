# Security and production-readiness review

Record at least 8 concrete risks or improvements relevant to your final solution.
This is a review requirement, not the number of hidden faults.

For each finding:
- Risk and evidence:
- Impact:
- Implemented fix / commit:
- Production follow-up:
- How to verify:

Cover secrets, ports, container user, image selection, networks, persistence/backup,
logging/monitoring and availability. Separate completed work from planned improvements.

## 1. Secrets exposure

- Risk and evidence: Database credentials are required by the application and PostgreSQL, so committing real secret values would expose them through Git history and the repository.
- Impact: Anyone with repository access could obtain the database credential and access PostgreSQL.
- Implemented fix / commit: Secrets are supplied through environment configuration rather than hard-coded into application code or the Docker image. Secret files are ignored by Git.
- Production follow-up: Use a managed secret store and rotate credentials regularly.
- How to verify: Inspect the repository and Dockerfile for hard-coded credentials and run `git status --short` after creating local secret files.


## 2. Unnecessary host ports

- Risk and evidence: Publishing application, PostgreSQL, or Redis ports would expose internal services directly to the host.
- Impact: Attackers or other local processes could bypass NGINX and reach internal services directly.
- Implemented fix / commit: Only NGINX is published on host port 8080; app, PostgreSQL, and Redis have no published host ports.
- Production follow-up: Keep internal services on private networks and use firewall rules or cloud security groups as an additional boundary.
- How to verify: Run `docker compose ps` and `docker inspect` to confirm only NGINX has a host port mapping.


## 3. Container user privileges

- Risk and evidence: Running application processes as root increases the impact of a container compromise.
- Impact: An attacker who compromises the application would have more privileges inside the container.
- Implemented fix / commit: The Flask application container runs as the non-root `app` user.
- Production follow-up: Continue using least privilege and remove unnecessary Linux capabilities.
- How to verify: Run `docker compose exec app-01 id` and confirm the process is not running as root.


## 4. Image selection and dependency risk

- Risk and evidence: Container images and application dependencies are external components that can contain vulnerabilities or receive breaking updates.
- Impact: A vulnerable dependency or image could introduce security issues or make the environment unreliable.
- Implemented fix / commit: Container image versions are pinned in the Compose configuration rather than relying on floating tags.
- Production follow-up: Add automated image/dependency vulnerability scanning and establish a patch/update process.
- How to verify: Inspect `docker-compose.yml` and `requirements.txt` for explicit versions and review image scan results when scanning is added.


## 5. Network isolation

- Risk and evidence: Allowing NGINX to access the backend network could expose PostgreSQL and Redis to a component that only needs to proxy application traffic.
- Impact: A compromise of NGINX could provide an unnecessary path toward backend services.
- Implemented fix / commit: NGINX is attached only to the frontend network; applications connect to both frontend and backend networks.
- Production follow-up: Keep network segmentation and add explicit firewall/network policies where the deployment platform supports them.
- How to verify: Inspect container network attachments and confirm NGINX is not connected to the backend network.


## 6. Data persistence and backup

- Risk and evidence: Database data can be lost through storage failure or operator error even when a named volume is used.
- Impact: Application records could become unavailable or permanently lost.
- Implemented fix / commit: PostgreSQL uses the named `postgres-data` volume, and `backup.sh` creates a PostgreSQL dump. `restore.sh` restores the dump and now fails with a non-zero exit code when PostgreSQL reports an error.
- Production follow-up: Store backups outside the host, encrypt them, schedule them, and regularly perform restore drills.
- How to verify: Create a record, run `backup.sh`, and verify the backup contains the record; test restoration against a clean database.


## 7. Logging and monitoring

- Risk and evidence: Without monitoring, service failures and repeated HTTP errors can remain unnoticed until users report them.
- Impact: Availability problems and operational incidents may last longer and be harder to investigate.
- Implemented fix / commit: The solution keeps NGINX access/error logging and application logs, and the failure test measures HTTP successes and errors during a backend failure.
- Production follow-up: Centralize logs, add metrics and alerts for error rates, readiness failures, container restarts, and resource exhaustion.
- How to verify: Inspect NGINX/application logs and run `failure_test.py` to observe and measure traffic errors.


## 8. Availability and recovery

- Risk and evidence: A backend instance can fail, causing some requests to return errors while the remaining instance continues serving traffic.
- Impact: Users may experience intermittent failures during a backend outage.
- Implemented fix / commit: Two Flask instances run behind NGINX with restart policies, and `failure_test.py` stops `app-01`, measures traffic, restores it, and verifies recovery.
- Production follow-up: Improve upstream failure handling, add health-aware load balancing, monitoring and alerting, and consider additional application instances across failure domains.
- How to verify: Run `failure_test.py` and confirm traffic continues, errors are measured, and the recovered backend serves successfully afterward.


