#!/usr/bin/env python3
"""Candidate deliverable: implement environment validation; this is not a solution."""
import json
import sys
import urllib.request


BASE_URL = "http://localhost:8080"


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
