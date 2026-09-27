#!/usr/bin/env python3
"""Candidate deliverable: stop one backend, measure traffic, restore it and verify."""

import subprocess
import time

BACKEND = "app-01"
REQUESTS = 10
def run(command):
    return subprocess.run(command, check=True)

def check_health():
    result = subprocess.run(
        ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "http://localhost:8080/health"],
        capture_output=True,
        text=True,
        check=False,
    )
    return result.stdout
if __name__ == "__main__":

    run(["docker", "compose", "stop", BACKEND])
    statuses = []

    for _ in range(REQUESTS):
        statuses.append(check_health())

    print("During failure:", statuses.count("200"), "successes,", REQUESTS - statuses.count("200"), "errors")

    run(["docker", "compose", "start", BACKEND])
    time.sleep(5)
    print("HTTP status after recovery:", check_health())
