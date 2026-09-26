# Technical decisions

Record at least 5 decisions. Include assumptions and limits.

## Decision
- Choice:
- Why:
- Alternative:
- Trade-off:
- Evidence / commit:
- Production improvement:

Cover your base image, health checks, networks, timeouts/retries, restart/resource settings,
storage and any other meaningful choices.


## Decision 1 — Redis persistence

- Choice: Keep Redis persistence disabled for the current assessment setup.
- Why: The assessment requires Redis persistence where appropriate, but it does not explicitly require the `/counter` value to survive a Redis restart. PostgreSQL is the persistent store for `/records`, while Redis is used for the application counter.
- Alternative: Enable Redis AOF or snapshot persistence.
- Trade-off: Keeping persistence disabled is simpler and avoids adding unnecessary storage configuration, but Redis counter data would be lost if Redis restarts.
- Evidence / commit: Runtime check showed `appendonly` is `no` and the `save` configuration is empty; `/counter` stores the value in Redis under `barq:requests`.
- Production improvement: If the counter becomes business-critical, enable Redis persistence and define an explicit recovery requirement.


## Decision 2 — Restart policies

- Choice: Use `unless-stopped` for NGINX, both Flask app instances, PostgreSQL, and Redis.
- Why: The assessment requires restart policies, and these services should recover automatically from an unexpected container or host restart while still allowing an intentional stop to remain stopped.
- Alternative: Keep `restart: "no"` or use `always`.
- Trade-off: Automatic recovery improves availability, but it can also restart a service repeatedly when there is a persistent configuration or dependency failure.
- Evidence / commit: Runtime inspection showed `no` for the app containers and no explicit restart policy for PostgreSQL, Redis, and NGINX.
- Production improvement: Add monitoring and restart-loop alerts so repeated failures are detected instead of relying only on Docker restarts.## Decision 2 — Restart policies
- Choice: Use `unless-stopped` for NGINX, both Flask app instances, PostgreSQL, and Redis.
- Why: The assessment requires restart policies, and these services should recover automatically from an unexpected container or host restart while still allowing an intentional stop to remain stopped.
- Alternative: Keep `restart: "no"` or use `always`.
- Trade-off: Automatic recovery improves availability, but it can also restart a service repeatedly when there is a persistent configuration or dependency failure.
- Evidence / commit: Runtime inspection showed `no` for the app containers and no explicit restart policy for PostgreSQL, Redis, and NGINX.
- Production improvement: Add monitoring and restart-loop alerts so repeated failures are detected instead of relying only on Docker restarts.
