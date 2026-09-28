# Log analysis

Use all three supplied logs. Answer every question with commands/scripts and actual output.

1. What UTC interval is covered? How many valid, malformed and duplicate lines are in each file?
2. How many distinct client requests occurred? How did you deduplicate and avoid counting retries twice?
3. What are the final client status counts and error rate? State your denominator.
4. Which paths, time windows and backends account for the failures?
5. What are the median and p95 client latencies? State the percentile method and units.
6. Which requests retried upstream? How many succeeded after retrying?
7. Build an incident timeline using evidence from access, error AND application logs.
8. Show one correlated failed request and one successful request. Include IDs and timestamps.
9. Which errors appear to be proxy/connectivity issues versus dependency/application issues? What proves it?
10. What do the logs not prove? What would you check next in a running environment?

## Commands / scripts
## Results
## Timeline and correlated examples
## Conclusions and limits


### 1. Parsing and time range

The supplied logs contain synthetic UTC data covering 2026-08-20T11:00:00.015Z through 2026-08-20T11:29:57.578Z in the JSON access and application logs. Automated JSON parsing found 725 valid access records and 1 malformed access record, plus 729 valid application records and 1 malformed application record. The error.log file contains 68 NGINX diagnostic text records and was analyzed as text rather than JSON. Malformed JSON records were excluded from JSON-based calculations.


### 2. Distinct client requests and deduplication

The access log contains 725 valid records but 720 distinct request IDs. Five request IDs (`lab-000121`, `lab-000241`, `lab-000361`, `lab-000481`, and `lab-000601`) occur twice. Inspection showed that each pair is an exact duplicate with the same timestamp, path, status, upstream, request time and client. Therefore, each pair was counted once as a client request, giving 720 distinct client requests. These records were treated as duplicate log records rather than separate retries.


### 3. Client status counts and error rate

After removing the five exact duplicate access records, the 720 distinct client requests had these final status counts:

- 200: 615
- 404: 10
- 502: 40
- 503: 47
- 504: 8

The client-visible non-200 count was 105 out of 720 distinct requests. Using non-200 responses as the error-rate definition, the client error rate was 105/720 = 14.58%. The 404 responses are included in this non-200 rate; they are separated from the 502/503/504 proxy/backend failures in the failure analysis.


### 4. Failure paths, time window and backends

The 502/503/504 failures affected `/`, `/counter`, `/health`, `/ready`, and `/records`.

By path and status:
- `/`: 10 × 502
- `/counter`: 10 × 502, 16 × 503
- `/health`: 10 × 502
- `/ready`: 23 × 503
- `/records`: 10 × 502, 8 × 503, 8 × 504

The 95 proxy/backend failures (502/503/504) were associated with upstream `172.23.0.11:8080` in 27 records and `172.23.0.12:8080` in 68 records.

The first client-visible 502/503/504 was at 2026-08-20T11:05:02.503Z (`lab-000122`), and the last was at 2026-08-20T11:26:47.001Z (`lab-000643`). This defines the observed client-visible failure window in the supplied access log.


### 5. Client latency

Using the `request_time` field from the access log, where the README defines the unit as seconds:

- Median request latency: 0.054 seconds (54 ms)
- p95 request latency: 2.001 seconds (2001 ms)

The median was calculated from the sorted `request_time` values. The p95 was calculated using the nearest-rank-style index `ceil(0.95 × N)` on the sorted values. These statistics use the recorded access-log requests, including the raw log records before duplicate removal.


### 6. Upstream retries

There were 19 access-log records with multiple upstream attempts. All 19 had an upstream status sequence of `502, 200`, meaning each request initially encountered a 502 upstream response and subsequently succeeded with HTTP 200.

Therefore, 19 requests retried upstream and 19 succeeded after retrying.


### 7. Incident timeline

- 11:05:02.503Z — `lab-000122` received HTTP 502 for `/health`. The upstream was `172.23.0.12:8080`.
- 11:05:02 — NGINX reported `connect() failed (111: Connection refused)` for `lab-000122` while connecting to `172.23.0.12:8080`.
- 11:05:05–11:05:35 — application logs show `app-01` successfully processing `/health`, `/ready`, `/records`, `/counter`, `/instance`, `/`, and `/health`.
- 11:12:09.524Z — application log shows the first observed Redis `TimeoutError` dependency event (`lab-000292`, `app-02`).
- 11:20:07.540Z — application log shows the first observed PostgreSQL `InvalidPassword` dependency event (`lab-000484`, `app-02`).
- 11:26:14 — NGINX reported an upstream timeout for `/records` against `172.23.0.12:8080`.
- 11:26:17 — NGINX reported an upstream timeout for `/records` against `172.23.0.11:8080`.
- 11:26:47.001Z — last observed client-facing 504 (`lab-000643`) for `/records` against `172.23.0.11:8080`.
- 11:30:00 — NGINX recorded a log collector rotation notice; this is not treated as an incident failure.

The logs establish these observed events but do not establish a single ultimate root cause or prove that one failure pattern caused another.


### 8. Correlated failed and successful requests

#### Failed request: `lab-000122`

- Access log: `2026-08-20T11:05:02.503Z`, `GET /health`, HTTP 502, upstream `172.23.0.12:8080`, request time 0.003 seconds.
- Error log: `2026/08/20 11:05:02`, NGINX reported `connect() failed (111: Connection refused)` while connecting to `172.23.0.12:8080/health`.
- Application log: no record for `lab-000122`.

This correlation shows a client-visible 502 associated with an NGINX upstream connection refusal, with no corresponding application request record in the supplied application log.

#### Successful request: `lab-000002`

- Access log: `2026-08-20T11:00:02.532Z`, `GET /health`, HTTP 200, upstream `172.23.0.12:8080`, request time 0.032 seconds.
- Application log: `2026-08-20T11:00:02.532Z`, `app-02`, `GET /health`, HTTP 200, duration 32.0 ms.

This correlation shows a successful request reaching `app-02` and returning HTTP 200.


### 9. Proxy/connectivity versus dependency/application errors

The NGINX error log contains explicit proxy/connectivity failures. Starting at 11:05:02, it repeatedly reports `connect() failed (111: Connection refused)` while connecting to upstream `172.23.0.12:8080`. Later, at 11:26, it reports `upstream timed out (110: Operation timed out) while reading response header from upstream`, affecting both `172.23.0.12:8080` and `172.23.0.11:8080`.

The application log separately contains dependency errors:
- 47 Redis `TimeoutError` dependency events.
- 16 PostgreSQL `InvalidPassword` dependency events.
- These errors occur on both `app-01` and `app-02`.

The evidence therefore distinguishes proxy/connectivity errors from application dependency errors. However, the supplied logs do not prove that any one of these failure types was the ultimate root cause of the others.


### 10. Limits of the evidence

The supplied logs do not prove the ultimate root cause of the incident. They show observed client failures, NGINX connection refusals and upstream timeouts, Redis timeout errors, and PostgreSQL authentication errors, but they do not show container lifecycle events, deployment changes, configuration changes, or the reason the affected dependencies became unhealthy.

The logs also do not prove that the Redis failures caused the NGINX connection refusals, or that the PostgreSQL authentication failures caused the later upstream timeouts. Those relationships would require additional evidence.

In a running environment, the next checks would include container/service health and restart history, application and dependency configuration, PostgreSQL and Redis service logs, network connectivity between services, resource utilization, and deployment/configuration changes around the incident period.
