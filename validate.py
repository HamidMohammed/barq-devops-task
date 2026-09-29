#!/usr/bin/env python3
"""Candidate deliverable: implement environment validation; this is not a solution."""
import json
import sys
import urllib.request
import subprocess

BASE_URL = "http://localhost:8090"
FRONTEND_NETWORK = "barq-assessment_frontend"
BACKEND_NETWORK = "barq-assessment_backend"
def docker_inspect(container):
    result = subprocess.run(
        ["docker", "inspect", container],
        capture_output=True,
        text=True,
        timeout=5,
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip())
    return json.loads(result.stdout)[0]

def check_url(path):
    url = BASE_URL + path
    try:
        with urllib.request.urlopen(url, timeout=3) as response:
            body = json.load(response)
            instance_header = response.headers.get("X-Instance-ID")
            if response.status == 200:
                if path == "/instance":
                    instance_id = body.get("instance_id")
                    if not instance_id:
                        print("FAIL /instance: missing instance_id")
                        return False
                    if instance_header != instance_id:
                         print("FAIL /instance: instance ID header does not match JSON")
                         return False
                print(f"PASS {path}")
                return True
            print(f"FAIL {path}: HTTP {response.status}")
            return False
    except Exception as exc:
        print(f"FAIL {path}: {exc}")
        return False

if __name__ == "__main__":
    nginx = docker_inspect("nginx")
    nginx_networks = set(nginx["NetworkSettings"]["Networks"])
    if nginx_networks == {FRONTEND_NETWORK}:
        print("PASS nginx network isolation")
    else:
        print(f"FAIL nginx network isolation: {nginx_networks}")
        sys.exit(1)
    for container in ["app-01", "app-02","app-03", "postgres", "redis"]:
        info = docker_inspect(container)
        networks = set(info["NetworkSettings"]["Networks"])

        if BACKEND_NETWORK in networks:
            print(f"PASS {container} backend network")
        else:
            print(f"FAIL {container} missing backend network")
            sys.exit(1)
    for container in ["app-01", "app-02","app-03", "postgres", "redis"]:
        info = docker_inspect(container)
        ports = info["NetworkSettings"]["Ports"]

        published = [
            binding
            for bindings in ports.values()
            if bindings
            for binding in bindings
        ]

        if not published:
            print(f"PASS {container} no host port")
        else:
            print(f"FAIL {container} has published ports: {published}")
            sys.exit(1)
    if not check_url("/"):
        sys.exit(1)
    if not check_url("/health"):
        sys.exit(1)

    if not check_url("/ready"):
        sys.exit(1)

    if not check_url("/instance"):
        sys.exit(1)

    if not check_url("/records"):
        sys.exit(1)

    if not check_url("/counter"):
        sys.exit(1)

    sys.exit(0)
